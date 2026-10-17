/*
 * SPDX-License-Identifier: MIT
 * vkz: the render pass (colour and depth loaded from BRender's buffers and
 * stored back), the pipeline (less-than depth test, colour interpolated in
 * screen space) and the command buffer.
 */
#include <stdio.h>

#include "vkz_ip.h"
#include "trz_frag.h"
#include "trz_vert.h"

static int fail(const char *what, VkResult r)
{
    fprintf(stderr, "vkz: %s failed (VkResult %d)\n", what, (int)r);
    return -1;
}

static int create_pass(vkz_context *c)
{
    VkAttachmentDescription a[2] = {{0}, {0}};
    VkAttachmentReference cref = {0, VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL};
    VkAttachmentReference dref = {1, VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL};
    VkSubpassDescription sub = {0};
    VkSubpassDependency dep[2] = {{0}, {0}};
    VkRenderPassCreateInfo pi = {VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO};
    VkFramebufferCreateInfo fi = {VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO};
    VkResult r;
    int i;
    for (i = 0; i < 2; i++) {
        a[i].format = i == 0 ? VKZ_COLOUR : VKZ_DEPTH;
        a[i].samples = VK_SAMPLE_COUNT_1_BIT;
        a[i].loadOp = VK_ATTACHMENT_LOAD_OP_LOAD;
        a[i].storeOp = VK_ATTACHMENT_STORE_OP_STORE;
        a[i].stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
        a[i].stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
        a[i].initialLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
        a[i].finalLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    }
    sub.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
    sub.colorAttachmentCount = 1;
    sub.pColorAttachments = &cref;
    sub.pDepthStencilAttachment = &dref;
    /* the uploads finish before the pass reads the attachments, and the pass
     * finishes before the copies out read them */
    dep[0].srcSubpass = VK_SUBPASS_EXTERNAL;
    dep[0].dstSubpass = 0;
    dep[0].srcStageMask = VK_PIPELINE_STAGE_TRANSFER_BIT;
    dep[0].dstStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT | VK_PIPELINE_STAGE_EARLY_FRAGMENT_TESTS_BIT;
    dep[0].srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    dep[0].dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_READ_BIT | VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT
                           | VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_READ_BIT | VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT;
    dep[1].srcSubpass = 0;
    dep[1].dstSubpass = VK_SUBPASS_EXTERNAL;
    dep[1].srcStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT | VK_PIPELINE_STAGE_LATE_FRAGMENT_TESTS_BIT;
    dep[1].dstStageMask = VK_PIPELINE_STAGE_TRANSFER_BIT;
    dep[1].srcAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT | VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT;
    dep[1].dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    pi.attachmentCount = 2;
    pi.pAttachments = a;
    pi.subpassCount = 1;
    pi.pSubpasses = &sub;
    pi.dependencyCount = 2;
    pi.pDependencies = dep;
    if ((r = vkCreateRenderPass(c->base->device, &pi, NULL, &c->pass)) != VK_SUCCESS) return fail("vkCreateRenderPass", r);
    fi.renderPass = c->pass;
    fi.attachmentCount = 2;
    fi.pAttachments = c->view;
    fi.width = c->width;
    fi.height = c->height;
    fi.layers = 1;
    if ((r = vkCreateFramebuffer(c->base->device, &fi, NULL, &c->framebuffer)) != VK_SUCCESS) return fail("vkCreateFramebuffer", r);
    return 0;
}

static VkShaderModule module(vkz_context *c, const uint32_t *code, size_t bytes)
{
    VkShaderModuleCreateInfo mi = {VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
    VkShaderModule m = VK_NULL_HANDLE;
    mi.codeSize = bytes;
    mi.pCode = code;
    if (vkCreateShaderModule(c->base->device, &mi, NULL, &m) != VK_SUCCESS) fail("vkCreateShaderModule", VK_ERROR_INITIALIZATION_FAILED);
    return m;
}

int vkz_pipeline_create(vkz_context *c)
{
    VkPushConstantRange push = {VK_SHADER_STAGE_VERTEX_BIT, 0, 2 * sizeof(float)};
    VkPipelineLayoutCreateInfo li = {VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    VkPipelineShaderStageCreateInfo st[2] = {{VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO}, {VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO}};
    VkVertexInputBindingDescription bind = {0, sizeof(vkz_vertex), VK_VERTEX_INPUT_RATE_VERTEX};
    VkVertexInputAttributeDescription attr[2] = {{0, 0, VK_FORMAT_R32G32B32_SFLOAT, 0}, {1, 0, VK_FORMAT_R32G32B32_SFLOAT, 3 * sizeof(float)}};
    VkPipelineVertexInputStateCreateInfo vin = {VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};
    VkPipelineInputAssemblyStateCreateInfo ia = {VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};
    VkViewport vp = {0, 0, (float)c->width, (float)c->height, 0, 1};
    VkRect2D sc = {{0, 0}, {c->width, c->height}};
    VkPipelineViewportStateCreateInfo vps = {VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO};
    VkPipelineRasterizationStateCreateInfo rs = {VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO};
    VkPipelineMultisampleStateCreateInfo ms = {VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO};
    VkPipelineDepthStencilStateCreateInfo ds = {VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO};
    VkPipelineColorBlendAttachmentState blend = {0};
    VkPipelineColorBlendStateCreateInfo cb = {VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};
    VkGraphicsPipelineCreateInfo gi = {VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};
    VkResult r;
    if (create_pass(c) != 0) return -1;
    li.pushConstantRangeCount = 1;
    li.pPushConstantRanges = &push;
    if ((r = vkCreatePipelineLayout(c->base->device, &li, NULL, &c->layout)) != VK_SUCCESS) return fail("vkCreatePipelineLayout", r);
    st[0].stage = VK_SHADER_STAGE_VERTEX_BIT;
    st[0].module = module(c, trz_vert, sizeof(trz_vert));
    st[0].pName = "main";
    st[1].stage = VK_SHADER_STAGE_FRAGMENT_BIT;
    st[1].module = module(c, trz_frag, sizeof(trz_frag));
    st[1].pName = "main";
    if (st[0].module == VK_NULL_HANDLE || st[1].module == VK_NULL_HANDLE) return -1;
    vin.vertexBindingDescriptionCount = 1;
    vin.pVertexBindingDescriptions = &bind;
    vin.vertexAttributeDescriptionCount = 2;
    vin.pVertexAttributeDescriptions = attr;
    ia.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
    vps.viewportCount = 1;
    vps.pViewports = &vp;
    vps.scissorCount = 1;
    vps.pScissors = &sc;
    rs.polygonMode = VK_POLYGON_MODE_FILL;
    rs.cullMode = VK_CULL_MODE_NONE;
    rs.frontFace = VK_FRONT_FACE_COUNTER_CLOCKWISE;
    rs.lineWidth = 1.0f;
    ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;
    ds.depthTestEnable = VK_TRUE;
    ds.depthWriteEnable = VK_TRUE;
    ds.depthCompareOp = VK_COMPARE_OP_LESS;
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
    gi.pDepthStencilState = &ds;
    gi.pColorBlendState = &cb;
    gi.layout = c->layout;
    gi.renderPass = c->pass;
    r = vkCreateGraphicsPipelines(c->base->device, VK_NULL_HANDLE, 1, &gi, NULL, &c->pipeline);
    vkDestroyShaderModule(c->base->device, st[0].module, NULL);
    vkDestroyShaderModule(c->base->device, st[1].module, NULL);
    return r == VK_SUCCESS ? 0 : fail("vkCreateGraphicsPipelines", r);
}

void vkz_pipeline_destroy(vkz_context *c)
{
    VkDevice d = c->base->device;
    if (c->pipeline) vkDestroyPipeline(d, c->pipeline, NULL);
    if (c->layout) vkDestroyPipelineLayout(d, c->layout, NULL);
    if (c->framebuffer) vkDestroyFramebuffer(d, c->framebuffer, NULL);
    if (c->pass) vkDestroyRenderPass(d, c->pass, NULL);
}

/* Copy between the staging buffers and the images, in the given direction. */
static void copy(vkz_context *c, VkCommandBuffer cmd, int in)
{
    int i;
    for (i = 0; i < 2; i++) {
        VkBufferImageCopy region = {0};
        region.imageSubresource.aspectMask = i == 0 ? VK_IMAGE_ASPECT_COLOR_BIT : VK_IMAGE_ASPECT_DEPTH_BIT;
        region.imageSubresource.layerCount = 1;
        region.imageExtent.width = c->width;
        region.imageExtent.height = c->height;
        region.imageExtent.depth = 1;
        if (in) vkCmdCopyBufferToImage(cmd, c->staging[i], c->image[i], VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
        else vkCmdCopyImageToBuffer(cmd, c->image[i], VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, c->staging[i], 1, &region);
    }
}

void vkz_record(vkz_context *c, VkCommandBuffer cmd, VkBuffer vb, uint32_t count)
{
    VkCommandBufferBeginInfo bi = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    VkImageMemoryBarrier to_dst[2] = {{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER}, {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER}};
    VkMemoryBarrier to_host = {VK_STRUCTURE_TYPE_MEMORY_BARRIER};
    VkRenderPassBeginInfo rp = {VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO};
    VkDeviceSize offset = 0;
    float size[2] = {(float)c->width, (float)c->height};
    int i;
    bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cmd, &bi);
    for (i = 0; i < 2; i++) {
        to_dst[i].dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
        to_dst[i].oldLayout = VK_IMAGE_LAYOUT_UNDEFINED;
        to_dst[i].newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
        to_dst[i].srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
        to_dst[i].dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
        to_dst[i].image = c->image[i];
        to_dst[i].subresourceRange.aspectMask = i == 0 ? VK_IMAGE_ASPECT_COLOR_BIT : VK_IMAGE_ASPECT_DEPTH_BIT;
        to_dst[i].subresourceRange.levelCount = 1;
        to_dst[i].subresourceRange.layerCount = 1;
    }
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 2, to_dst);
    copy(c, cmd, 1);
    rp.renderPass = c->pass;
    rp.framebuffer = c->framebuffer;
    rp.renderArea.extent.width = c->width;
    rp.renderArea.extent.height = c->height;
    vkCmdBeginRenderPass(cmd, &rp, VK_SUBPASS_CONTENTS_INLINE);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_GRAPHICS, c->pipeline);
    vkCmdPushConstants(cmd, c->layout, VK_SHADER_STAGE_VERTEX_BIT, 0, sizeof(size), size);
    vkCmdBindVertexBuffers(cmd, 0, 1, &vb, &offset);
    vkCmdDraw(cmd, count, 1, 0, 0);
    vkCmdEndRenderPass(cmd);
    copy(c, cmd, 0);
    to_host.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    to_host.dstAccessMask = VK_ACCESS_HOST_READ_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_HOST_BIT, 0, 1, &to_host, 0, NULL, 0, NULL);
    vkEndCommandBuffer(cmd);
}
