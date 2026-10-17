/*
 * SPDX-License-Identifier: MIT
 * Inside the headless Vulkan rasteriser: shared between vk_offscreen.c and
 * vk_pipeline.c, not part of its interface.
 */
#ifndef VK_OFFSCREEN_IP_H
#define VK_OFFSCREEN_IP_H

#include <vulkan/vulkan.h>
#include "vk_offscreen.h"

#define VKO_FORMAT VK_FORMAT_R8G8B8A8_UNORM

struct vko_context {
    uint32_t         width, height;
    VkInstance       instance;
    VkPhysicalDevice gpu;
    uint32_t         queue_family;
    VkDevice         device;
    VkQueue          queue;
    VkCommandPool    pool;
    VkImage          image;
    VkDeviceMemory   image_memory;
    VkImageView      view;
    VkBuffer         readback;
    VkDeviceMemory   readback_memory;
    VkRenderPass     pass;
    VkFramebuffer    framebuffer;
    VkPipelineLayout layout;
    VkPipeline       pipeline;
};

int vko_memory_type(const vko_context *c, uint32_t bits, VkMemoryPropertyFlags want);
int vko_buffer(vko_context *c, VkDeviceSize size, VkBufferUsageFlags usage, VkBuffer *buf, VkDeviceMemory *mem);

int  vko_pipeline_create(vko_context *c);
void vko_pipeline_destroy(vko_context *c);

#endif
