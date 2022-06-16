package com.macro.mall.portal.dto;

import com.macro.mall.portal.domain.HomeContentResult;
import io.swagger.annotations.ApiModelProperty;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 用户推荐反馈dto
 */
@Data
@EqualsAndHashCode(callSuper = false)
public class ImgProcessDto {
    @ApiModelProperty("处理前文件访问URL")
    private String url;
    @ApiModelProperty("处理后文件访问URL")
    private String lurl;
    @ApiModelProperty("文件名称")
    private String name;
    @ApiModelProperty("获取推荐列表")
    private HomeContentResult homeContentResult;
}
