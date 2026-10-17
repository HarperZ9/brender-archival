/*
 * SPDX-License-Identifier: MIT
 * The render pass, the pipeline and the draw of the headless Vulkan
 * rasteriser. The shaders are compiled from tri.vert and tri.frag to SPIR-V
 * at build time (glslangValidator --vn) and included as arrays.
 */
#include <stdio.h>
#include <string.h>

#include "vk_offscreen_ip.h"
#include "tri_frag.h"
#include "tri_vert.h"

static int fail(const char *what, VkResult r)
{
    fprintf(stderr, "vk-offscreen: %s failed (VkResult %d)\n", what, (int)r);
    return -1;
}

static int create_pass(vko_context *c)
{
    VkAttachmentDescription a = {0};
    VkAttachmentReference ref = {0, VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL};
    VkSubpassDescription sub = {0};
    VkRenderPassCreateInfo pi = {VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO};
    VkFramebufferCreateInfo fi = {VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO};
    VkResult r;
    a.format = VKO_FORMAT;
    a.samples = VK_SAMPLE_COUNT_1_BIT;
    a.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
    a.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
    a.stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
    a.stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
    a.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    a.finalLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    sub.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
    sub.colorAttachmentCount = 1;
    sub.pColorAttachments = &ref;
    pi.attachmentCount = 1;
    pi.pAttachments = &a;
    pi.subpassCount = 1;
    pi.pSubpasses = &sub;
    if ((r = vkCreateRenderPass(c->device, &pi, NULL, &c->pass)) != VK_SUCCESS) return fail("vkCreateRenderPass", r);
    fi.renderPass = c->pass;
    fi.attachmentCount = 1;
    fi.pAttachments = &c->view;
    fi.width = c->width;
    fi.height = c->height;
    fi.layers = 1;
    if ((r = vkCreateFramebuffer(c->device, &fi, NULL, &c->framebuffer)) != VK_SUCCESS) return fail("vkCreateFramebuffer", r);
    return 0;
}

static VkShaderModule module(vko_context *c, const uint32_t *code, size_t bytes)
{
    VkShaderModuleCreateInfo mi = {VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
    VkShaderModule m = VK_NULL_HANDLE;
    mi.codeSize = bytes;
    mi.pCode = code;
    if (vkCreateShaderModule(c->device, &mi, NULL, &m) != VK_SUCCESS) fail("vkCreateShaderModule", VK_ERROR_INITIALIZATION_FAILED);
    return m;
}

int vko_pipeline_create(vko_context *c)
{
    VkPushConstantRange push = {VK_SHADER_STAGE_VERTEX_BIT, 0, 2 * sizeof(float)};
    VkPipelineLayoutCreateInfo li = {VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    VkPipelineShaderStageCreateInfo st[2] = {{VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO}, {VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO}};
    VkVertexInputBindingDescription bind = {0, sizeof(vko_vertex), VK_VERTEX_INPUT_RATE_VERTEX};
    VkVertexInputAttributeDescription attr[2] = {{0, 0, VK_FORMAT_R32G32_SFLOAT, 0}, {1, 0, VK_FORMAT_R32G32B32_SFLOAT, 2 * sizeof(float)}};
    VkPipelineVertexInputStateCreateInfo vin = {VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};
    VkPipelineInputAssemblyStateCreateInfo ia = {VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};
    VkViewport vp = {0, 0, 0, 0, 0, 1};
    VkRect2D sc = {{0, 0}, {0, 0}};
    VkPipelineViewportStateCreateInfo vps = {VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO};
    VkPipelineRasterizationStateCreateInfo rs = {VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO};
    VkPipelineMultisampleStateCreateInfo ms = {VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO};
    VkPipelineColorBlendAttachmentState blend = {0};
    VkPipelineColorBlendStateCreateInfo cb = {VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};
    VkGraphicsPipelineCreateInfo gi = {VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};
    VkResult r;
    if (create_pass(c) != 0) return -1;
    li.pushConstantRangeCount = 1;
    li.pPushConstantRanges = &push;
    if ((r = vkCreatePipelineLayout(c->device, &li, NULL, &c->layout)) != VK_SUCCESS) return fail("vkCreatePipelineLayout", r);
    st[0].stage = VK_SHADER_STAGE_VERTEX_BIT;
    st[0].module = module(c, tri_vert, sizeof(tri_vert));
    st[0].pName = "main";
    st[1].stage = VK_SHADER_STAGE_FRAGMENT_BIT;
    st[1].module = module(c, tri_frag, sizeof(tri_frag));
    st[1].pName = "main";
    if (st[0].module == VK_NULL_HANDLE || st[1].module == VK_NULL_HANDLE) return -1;
    vin.vertexBindingDescriptionCount = 1;
    vin.pVertexBindingDescriptions = &bind;
    vin.vertexAttributeDescriptionCount = 2;
    vin.pVertexAttributeDescriptions = attr;
    ia.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
    vp.width = (float)c->width;
    vp.height = (float)c->height;
    sc.extent.width = c->width;
    sc.extent.height = c->height;
    vps.viewportCount = 1;
    vps.pViewports = &vp;
    vps.scissorCount = 1;
    vps.pScissors = &sc;
    rs.polygonMode = VK_POLYGON_MODE_FILL;
    rs.cullMode = VK_CULL_MODE_NONE;
    rs.frontFace = VK_FRONT_FACE_COUNTER_CLOCKWISE;
    rs.lineWidth = 1.0f;
    ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;
    blend.colorWriteMask = 0xF;
    cb.attachmentCount = 1;
    cb.pAttachments = &blend;
    gi.stageCount = 2;
    gi.pStages = st;
    gi.pVertexInputState = &vin;
    gi.pInputAssemblyState = &ia;
    gi.pViewportState = &vps;
    gi.pRasterizationState = &rs;
    gi.pMultisampleState = &ms;
    gi.pColorBlendState = &cb;
    gi.layout = c->layout;
    gi.renderPass = c->pass;
    r = vkCreateGraphicsPipelines(c->device, VK_NULL_HANDLE, 1, &gi, NULL, &c->pipeline);
    vkDestroyShaderModule(c->device, st[0].module, NULL);
    vkDestroyShaderModule(c->device, st[1].module, NULL);
    return r == VK_SUCCESS ? 0 : fail("vkCreateGraphicsPipelines", r);
}

void vko_pipeline_destroy(vko_context *c)
{
    if (c->pipeline) vkDestroyPipeline(c->device, c->pipeline, NULL);
    if (c->layout) vkDestroyPipelineLayout(c->device, c->layout, NULL);
    if (c->framebuffer) vkDestroyFramebuffer(c->device, c->framebuffer, NULL);
    if (c->pass) vkDestroyRenderPass(c->device, c->pass, NULL);
}

static void record(vko_context *c, VkCommandBuffer cmd, VkBuffer vb, uint32_t count, float r, float g, float b)
{
    VkCommandBufferBeginInfo bi = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    VkRenderPassBeginInfo rp = {VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO};
    VkClearValue clear;
    VkBufferImageCopy copy = {0};
    VkDeviceSize offset = 0;
    float size[2] = {(float)c->width, (float)c->height};
    clear.color.float32[0] = r;
    clear.color.float32[1] = g;
    clear.color.float32[2] = b;
    clear.color.float32[3] = 1.0f;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cmd, &bi);
    rp.renderPass = c->pass;
    rp.framebuffer = c->framebuffer;
    rp.renderArea.extent.width = c->width;
    rp.renderArea.extent.height = c->height;
    rp.clearValueCount = 1;
    rp.pClearValues = &clear;
    vkCmdBeginRenderPass(cmd, &rp, VK_SUBPASS_CONTENTS_INLINE);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, c->pipeline);
    vkCmdPushConstants(cmd, c->layout, VK_SHADER_STAGE_VERTEX_BIT, 0, sizeof(size), size);
    vkCmdBindVertexBuffers(cmd, 0, 1, &vb, &offset);
    vkCmdDraw(cmd, count, 1, 0, 0);
    vkCmdEndRenderPass(cmd);
    copy.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    copy.imageSubresource.layerCount = 1;
    copy.imageExtent.width = c->width;
    copy.imageExtent.height = c->height;
    copy.imageExtent.depth = 1;
    vkCmdCopyImageToBuffer(cmd, c->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, c->readback, 1, &copy);
    vkEndCommandBuffer(cmd);
}

int vko_draw(vko_context *c, const vko_vertex *vertices, uint32_t count, float r, float g, float b, uint8_t *rgb)
{
    VkCommandBufferAllocateInfo ai = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
    VkSubmitInfo si = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
    VkCommandBuffer cmd;
    VkBuffer vb;
    VkDeviceMemory vm;
    void *p;
    uint32_t i;
    int ok = -1;
    if (count == 0 || vko_buffer(c, sizeof(vko_vertex) * count, VK_BUFFER_USAGE_VERTEX_BUFFER_BIT, &vb, &vm) != 0) return -1;
    vkMapMemory(c->device, vm, 0, VK_WHOLE_SIZE, 0, &p);
    memcpy(p, vertices, sizeof(vko_vertex) * count);
    vkUnmapMemory(c->device, vm);
    ai.commandPool = c->pool;
    ai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    ai.commandBufferCount = 1;
    if (vkAllocateCommandBuffers(c->device, &ai, &cmd) == VK_SUCCESS) {
        record(c, cmd, vb, count, r, g, b);
        si.commandBufferCount = 1;
        si.pCommandBuffers = &cmd;
        if (vkQueueSubmit(c->queue, 1, &si, VK_NULL_HANDLE) == VK_SUCCESS && vkQueueWaitIdle(c->queue) == VK_SUCCESS
            && vkMapMemory(c->device, c->readback_memory, 0, VK_WHOLE_SIZE, 0, &p) == VK_SUCCESS) {
            for (i = 0; i < c->width * c->height; i++)
                memcpy(rgb + i * 3, (const uint8_t *)p + i * 4, 3);
            vkUnmapMemory(c->device, c->readback_memory);
            ok = 0;
        }
        vkFreeCommandBuffers(c->device, c->pool, 1, &cmd);
    }
    vkDestroyBuffer(c->device, vb, NULL);
    vkFreeMemory(c->device, vm, NULL);
    return ok;
}
