/*
 * SPDX-License-Identifier: MIT
 * Inside vkz: shared by vkz.c and vkz_pipe.c.
 */
#ifndef VKZ_IP_H
#define VKZ_IP_H

#include "vk_offscreen_ip.h"
#include "vkz.h"

#define VKZ_COLOUR VK_FORMAT_B8G8R8A8_UNORM
#define VKZ_DEPTH  VK_FORMAT_D16_UNORM

struct vkz_context {
    vko_context     *base; /* instance, device, queue and command pool */
    uint32_t         width, height;
    VkImage          image[2]; /* colour, depth */
    VkDeviceMemory   image_memory[2];
    VkImageView      view[2];
    VkBuffer         staging[2];
    VkDeviceMemory   staging_memory[2];
    VkRenderPass     pass;
    VkFramebuffer    framebuffer;
    VkPipelineLayout layout;
    VkPipeline       pipeline;
};

int  vkz_pipeline_create(vkz_context *c);
void vkz_pipeline_destroy(vkz_context *c);
void vkz_record(vkz_context *c, VkCommandBuffer cmd, VkBuffer vb, uint32_t count);

#endif
