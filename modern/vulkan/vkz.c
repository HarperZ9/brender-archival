/*
 * SPDX-License-Identifier: MIT
 * vkz: the colour and depth images, their staging buffers, the copies in and
 * out, and the submit. The render pass and pipeline are in vkz_pipe.c.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "vkz_ip.h"

static int fail(const char *what, VkResult r)
{
    fprintf(stderr, "vkz: %s failed (VkResult %d)\n", what, (int)r);
    return -1;
}

static int make_image(vkz_context *c, int i, VkFormat format, VkImageUsageFlags usage, VkImageAspectFlags aspect)
{
    VkDevice d = c->base->device;
    VkImageCreateInfo ii = {VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
    VkImageViewCreateInfo vi = {VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    VkMemoryAllocateInfo ai = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    VkMemoryRequirements req;
    VkResult r;
    int type;
    ii.imageType = VK_IMAGE_TYPE_2D;
    ii.format = format;
    ii.extent.width = c->width;
    ii.extent.height = c->height;
    ii.extent.depth = 1;
    ii.mipLevels = 1;
    ii.arrayLayers = 1;
    ii.samples = VK_SAMPLE_COUNT_1_BIT;
    ii.tiling = VK_IMAGE_TILING_OPTIMAL;
    ii.usage = usage | VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;
    ii.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    if ((r = vkCreateImage(d, &ii, NULL, &c->image[i])) != VK_SUCCESS) return fail("vkCreateImage", r);
    vkGetImageMemoryRequirements(d, c->image[i], &req);
    if ((type = vko_memory_type(c->base, req.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)) < 0)
        type = vko_memory_type(c->base, req.memoryTypeBits, 0);
    ai.allocationSize = req.size;
    ai.memoryTypeIndex = (uint32_t)type;
    if ((r = vkAllocateMemory(d, &ai, NULL, &c->image_memory[i])) != VK_SUCCESS) return fail("vkAllocateMemory", r);
    vkBindImageMemory(d, c->image[i], c->image_memory[i], 0);
    vi.image = c->image[i];
    vi.viewType = VK_IMAGE_VIEW_TYPE_2D;
    vi.format = format;
    vi.subresourceRange.aspectMask = aspect;
    vi.subresourceRange.levelCount = 1;
    vi.subresourceRange.layerCount = 1;
    if ((r = vkCreateImageView(d, &vi, NULL, &c->view[i])) != VK_SUCCESS) return fail("vkCreateImageView", r);
    return vko_buffer(c->base, (VkDeviceSize)c->width * c->height * (i == 0 ? 4 : 2),
                      VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT, &c->staging[i], &c->staging_memory[i]);
}

vkz_context *vkz_create(uint32_t width, uint32_t height, char *device_name, size_t name_len)
{
    vkz_context *c = calloc(1, sizeof(*c));
    if (c == NULL) return NULL;
    c->width = width;
    c->height = height;
    if ((c->base = vko_create(width, height, device_name, name_len)) == NULL
        || make_image(c, 0, VKZ_COLOUR, VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT, VK_IMAGE_ASPECT_COLOR_BIT) != 0
        || make_image(c, 1, VKZ_DEPTH, VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT, VK_IMAGE_ASPECT_DEPTH_BIT) != 0
        || vkz_pipeline_create(c) != 0) {
        vkz_destroy(c);
        return NULL;
    }
    return c;
}

void vkz_destroy(vkz_context *c)
{
    int i;
    if (c == NULL) return;
    if (c->base && c->base->device) {
        VkDevice d = c->base->device;
        vkDeviceWaitIdle(d);
        vkz_pipeline_destroy(c);
        for (i = 0; i < 2; i++) {
            if (c->staging[i]) vkDestroyBuffer(d, c->staging[i], NULL);
            if (c->staging_memory[i]) vkFreeMemory(d, c->staging_memory[i], NULL);
            if (c->view[i]) vkDestroyImageView(d, c->view[i], NULL);
            if (c->image[i]) vkDestroyImage(d, c->image[i], NULL);
            if (c->image_memory[i]) vkFreeMemory(d, c->image_memory[i], NULL);
        }
    }
    vko_destroy(c->base);
    free(c);
}

/* BRender's rows into the staging buffers (colour B, G, R to B, G, R, A),
 * or back again. */
static void stage(vkz_context *c, uint8_t *bgr, size_t cs, uint8_t *depth, size_t ds, int back)
{
    VkDevice d = c->base->device;
    uint8_t *p[2];
    uint32_t x, y;
    vkMapMemory(d, c->staging_memory[0], 0, VK_WHOLE_SIZE, 0, (void **)&p[0]);
    vkMapMemory(d, c->staging_memory[1], 0, VK_WHOLE_SIZE, 0, (void **)&p[1]);
    for (y = 0; y < c->height; y++) {
        uint8_t *row = bgr + y * cs, *img = p[0] + (size_t)y * c->width * 4;
        for (x = 0; x < c->width; x++) {
            if (back) memcpy(row + x * 3, img + x * 4, 3);
            else { memcpy(img + x * 4, row + x * 3, 3); img[x * 4 + 3] = 255; }
        }
        if (back) memcpy(depth + y * ds, p[1] + (size_t)y * c->width * 2, (size_t)c->width * 2);
        else memcpy(p[1] + (size_t)y * c->width * 2, depth + y * ds, (size_t)c->width * 2);
    }
    vkUnmapMemory(d, c->staging_memory[0]);
    vkUnmapMemory(d, c->staging_memory[1]);
}

int vkz_draw(vkz_context *c, const vkz_vertex *v, uint32_t count, uint8_t *bgr, size_t colour_stride, uint8_t *depth,
             size_t depth_stride)
{
    VkDevice d = c->base->device;
    VkCommandBufferAllocateInfo ai = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
    VkSubmitInfo si = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
    VkCommandBuffer cmd;
    VkBuffer vb;
    VkDeviceMemory vm;
    void *p;
    int ok = -1;
    if (count == 0) return 0;
    if (vko_buffer(c->base, sizeof(vkz_vertex) * count, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT, &vb, &vm) != 0) return -1;
    vkMapMemory(d, vm, 0, VK_WHOLE_SIZE, 0, &p);
    memcpy(p, v, sizeof(vkz_vertex) * count);
    vkUnmapMemory(d, vm);
    stage(c, bgr, colour_stride, depth, depth_stride, 0);
    ai.commandPool = c->base->pool;
    ai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    ai.commandBufferCount = 1;
    if (vkAllocateCommandBuffers(d, &ai, &cmd) == VK_SUCCESS) {
        vkz_record(c, cmd, vb, count);
        si.commandBufferCount = 1;
        si.pCommandBuffers = &cmd;
        if (vkQueueSubmit(c->base->queue, 1, &si, VK_NULL_HANDLE) == VK_SUCCESS && vkQueueWaitIdle(c->base->queue) == VK_SUCCESS) {
            stage(c, bgr, colour_stride, depth, depth_stride, 1);
            ok = 0;
        }
        vkFreeCommandBuffers(d, c->base->pool, 1, &cmd);
    }
    vkDestroyBuffer(d, vb, NULL);
    vkFreeMemory(d, vm, NULL);
    return ok;
}
