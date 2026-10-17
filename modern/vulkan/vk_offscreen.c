/*
 * SPDX-License-Identifier: MIT
 * A headless Vulkan rasteriser: the instance, the device, the image and the
 * buffers. The render pass and pipeline are in vk_pipeline.c.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "vk_offscreen_ip.h"

static int fail(const char *what, VkResult r)
{
    fprintf(stderr, "vk-offscreen: %s failed (VkResult %d)\n", what, (int)r);
    return -1;
}

int vko_memory_type(const vko_context *c, uint32_t bits, VkMemoryPropertyFlags want)
{
    VkPhysicalDeviceMemoryProperties p;
    uint32_t i;
    vkGetPhysicalDeviceMemoryProperties(c->gpu, &p);
    for (i = 0; i < p.memoryTypeCount; i++)
        if ((bits & (1u << i)) && (p.memoryTypes[i].propertyFlags & want) == want)
            return (int)i;
    return -1;
}

int vko_buffer(vko_context *c, VkDeviceSize size, VkBufferUsageFlags usage, VkBuffer *buf, VkDeviceMemory *mem)
{
    VkBufferCreateInfo bi = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    VkMemoryAllocateInfo ai = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    VkMemoryRequirements req;
    VkResult r;
    int type;
    bi.size = size;
    bi.usage = usage;
    bi.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    if ((r = vkCreateBuffer(c->device, &bi, NULL, buf)) != VK_SUCCESS) return fail("vkCreateBuffer", r);
    vkGetBufferMemoryRequirements(c->device, *buf, &req);
    type = vko_memory_type(c, req.memoryTypeBits, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
    if (type < 0) return fail("finding host-visible memory", VK_ERROR_OUT_OF_DEVICE_MEMORY);
    ai.allocationSize = req.size;
    ai.memoryTypeIndex = (uint32_t)type;
    if ((r = vkAllocateMemory(c->device, &ai, NULL, mem)) != VK_SUCCESS) return fail("vkAllocateMemory", r);
    return vkBindBufferMemory(c->device, *buf, *mem, 0) == VK_SUCCESS ? 0 : -1;
}

static int pick_device(vko_context *c, char *name, size_t name_len)
{
    VkPhysicalDevice gpus[16];
    uint32_t n = 16, i, q, nq;
    const char *want = getenv("VKO_DEVICE_TYPE");
    int cpu_only = want != NULL && strcmp(want, "cpu") == 0;
    if (vkEnumeratePhysicalDevices(c->instance, &n, gpus) < 0 || n == 0) return fail("finding a Vulkan device", VK_ERROR_INITIALIZATION_FAILED);
    for (i = 0; i < n; i++) {
        VkPhysicalDeviceProperties props;
        VkQueueFamilyProperties fams[16];
        vkGetPhysicalDeviceProperties(gpus[i], &props);
        if (cpu_only && props.deviceType != VK_PHYSICAL_DEVICE_TYPE_CPU) continue;
        nq = 16;
        vkGetPhysicalDeviceQueueFamilyProperties(gpus[i], &nq, fams);
        for (q = 0; q < nq; q++) {
            if (fams[q].queueFlags & VK_QUEUE_GRAPHICS_BIT) {
                c->gpu = gpus[i];
                c->queue_family = q;
                snprintf(name, name_len, "%s", props.deviceName);
                return 0;
            }
        }
    }
    return fail(cpu_only ? "finding a CPU Vulkan device (VKO_DEVICE_TYPE=cpu)" : "finding a device that can draw", VK_ERROR_INITIALIZATION_FAILED);
}

static int create_device(vko_context *c)
{
    float priority = 1.0f;
    VkDeviceQueueCreateInfo qi = {VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
    VkDeviceCreateInfo di = {VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
    VkCommandPoolCreateInfo pi = {VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
    VkResult r;
    qi.queueFamilyIndex = c->queue_family;
    qi.queueCount = 1;
    qi.pQueuePriorities = &priority;
    di.queueCreateInfoCount = 1;
    di.pQueueCreateInfos = &qi;
    if ((r = vkCreateDevice(c->gpu, &di, NULL, &c->device)) != VK_SUCCESS) return fail("vkCreateDevice", r);
    vkGetDeviceQueue(c->device, c->queue_family, 0, &c->queue);
    pi.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
    pi.queueFamilyIndex = c->queue_family;
    if ((r = vkCreateCommandPool(c->device, &pi, NULL, &c->pool)) != VK_SUCCESS) return fail("vkCreateCommandPool", r);
    return 0;
}

static int create_image(vko_context *c)
{
    VkImageCreateInfo ii = {VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
    VkImageViewCreateInfo vi = {VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    VkMemoryAllocateInfo ai = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    VkMemoryRequirements req;
    VkResult r;
    int type;
    ii.imageType = VK_IMAGE_TYPE_2D;
    ii.format = VKO_FORMAT;
    ii.extent.width = c->width;
    ii.extent.height = c->height;
    ii.extent.depth = 1;
    ii.mipLevels = 1;
    ii.arrayLayers = 1;
    ii.samples = VK_SAMPLE_COUNT_1_BIT;
    ii.tiling = VK_IMAGE_TILING_OPTIMAL;
    ii.usage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
    ii.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    if ((r = vkCreateImage(c->device, &ii, NULL, &c->image)) != VK_SUCCESS) return fail("vkCreateImage", r);
    vkGetImageMemoryRequirements(c->device, c->image, &req);
    if ((type = vko_memory_type(c, req.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)) < 0)
        type = vko_memory_type(c, req.memoryTypeBits, 0);
    ai.allocationSize = req.size;
    ai.memoryTypeIndex = (uint32_t)type;
    if ((r = vkAllocateMemory(c->device, &ai, NULL, &c->image_memory)) != VK_SUCCESS) return fail("vkAllocateMemory (image)", r);
    vkBindImageMemory(c->device, c->image, c->image_memory, 0);
    vi.image = c->image;
    vi.viewType = VK_IMAGE_VIEW_TYPE_2D;
    vi.format = VKO_FORMAT;
    vi.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    vi.subresourceRange.levelCount = 1;
    vi.subresourceRange.layerCount = 1;
    if ((r = vkCreateImageView(c->device, &vi, NULL, &c->view)) != VK_SUCCESS) return fail("vkCreateImageView", r);
    return vko_buffer(c, (VkDeviceSize)c->width * c->height * 4, VK_BUFFER_USAGE_TRANSFER_DST_BIT, &c->readback, &c->readback_memory);
}

vko_context *vko_create(uint32_t width, uint32_t height, char *device_name, size_t name_len)
{
    VkApplicationInfo app = {VK_STRUCTURE_TYPE_APPLICATION_INFO};
    VkInstanceCreateInfo ci = {VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    vko_context *c = calloc(1, sizeof(*c));
    VkResult r;
    if (c == NULL) return NULL;
    c->width = width;
    c->height = height;
    app.pApplicationName = "brender-vk-offscreen";
    app.apiVersion = VK_API_VERSION_1_0;
    ci.pApplicationInfo = &app;
    if ((r = vkCreateInstance(&ci, NULL, &c->instance)) != VK_SUCCESS) {
        fail("vkCreateInstance", r);
        free(c);
        return NULL;
    }
    if (pick_device(c, device_name, name_len) != 0 || create_device(c) != 0 || create_image(c) != 0 || vko_pipeline_create(c) != 0) {
        vko_destroy(c);
        return NULL;
    }
    return c;
}

void vko_destroy(vko_context *c)
{
    if (c == NULL) return;
    if (c->device) {
        vkDeviceWaitIdle(c->device);
        vko_pipeline_destroy(c);
        if (c->readback) vkDestroyBuffer(c->device, c->readback, NULL);
        if (c->readback_memory) vkFreeMemory(c->device, c->readback_memory, NULL);
        if (c->view) vkDestroyImageView(c->device, c->view, NULL);
        if (c->image) vkDestroyImage(c->device, c->image, NULL);
        if (c->image_memory) vkFreeMemory(c->device, c->image_memory, NULL);
        if (c->pool) vkDestroyCommandPool(c->device, c->pool, NULL);
        vkDestroyDevice(c->device, NULL);
    }
    if (c->instance) vkDestroyInstance(c->instance, NULL);
    free(c);
}
