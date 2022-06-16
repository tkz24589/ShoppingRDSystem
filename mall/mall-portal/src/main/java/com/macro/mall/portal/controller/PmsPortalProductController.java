package com.macro.mall.portal.controller;

import cn.hutool.core.collection.CollUtil;
import cn.hutool.json.JSONUtil;
import com.macro.mall.common.api.CommonPage;
import com.macro.mall.common.api.CommonResult;
import com.macro.mall.model.PmsProduct;
import com.macro.mall.portal.domain.HomeContentResult;
import com.macro.mall.portal.domain.PmsPortalProductDetail;
import com.macro.mall.portal.domain.PmsProductCategoryNode;
import com.macro.mall.portal.dto.BucketPolicyConfigDto;
import com.macro.mall.portal.dto.ImgProcessDto;
import com.macro.mall.portal.dto.MinioUploadDto;
import com.macro.mall.portal.service.PmsPortalProductService;
import io.minio.*;
import io.minio.errors.MinioException;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiOperation;
import org.python.antlr.ast.Str;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * 前台商品管理Controller
 * Created by macro on 2020/4/6.
 */
@Controller
@Api(tags = "PmsPortalProductController", description = "前台商品管理")
@RequestMapping("/product")
public class PmsPortalProductController {

    private static final Logger LOGGER = LoggerFactory.getLogger(PmsPortalProductController.class);
    @Value("${minio.endpoint}")
    private String ENDPOINT;
    @Value("${minio.bucketName}")
    private String BUCKET_NAME;
    @Value("${minio.accessKey}")
    private String ACCESS_KEY;
    @Value("${minio.secretKey}")
    private String SECRET_KEY;

    @Autowired
    private PmsPortalProductService portalProductService;

    @ApiOperation(value = "综合搜索、筛选、排序")
    @ApiImplicitParam(name = "sort", value = "排序字段:0->按相关度；1->按新品；2->按销量；3->价格从低到高；4->价格从高到低",
            defaultValue = "0", allowableValues = "0,1,2,3,4", paramType = "query", dataType = "integer")
    @RequestMapping(value = "/search", method = RequestMethod.GET)
    @ResponseBody
    public CommonResult<CommonPage<PmsProduct>> search(@RequestParam(required = false) String keyword,
                                                       @RequestParam(required = false) Long brandId,
                                                       @RequestParam(required = false) Long productCategoryId,
                                                       @RequestParam(required = false, defaultValue = "0") Integer pageNum,
                                                       @RequestParam(required = false, defaultValue = "5") Integer pageSize,
                                                       @RequestParam(required = false, defaultValue = "0") Integer sort) {
        List<PmsProduct> productList = portalProductService.search(keyword, brandId, productCategoryId, pageNum, pageSize, sort);
        return CommonResult.success(CommonPage.restPage(productList));
    }

    @ApiOperation("以树形结构获取所有商品分类")
    @RequestMapping(value = "/categoryTreeList", method = RequestMethod.GET)
    @ResponseBody
    public CommonResult<List<PmsProductCategoryNode>> categoryTreeList() {
        List<PmsProductCategoryNode> list = portalProductService.categoryTreeList();
        return CommonResult.success(list);
    }

    @ApiOperation("获取前台商品详情")
    @RequestMapping(value = "/detail", method = RequestMethod.GET)
    @ResponseBody
    public CommonResult<PmsPortalProductDetail> detail(@RequestParam(required = false) Long productId) {
        PmsPortalProductDetail productDetail = portalProductService.detail(productId);
        return CommonResult.success(productDetail);
    }

    @ApiOperation("获取用户上传图像")
    @RequestMapping(value = "/delPic", method = RequestMethod.POST)
    @ResponseBody
    public CommonResult delPic(@RequestParam(required = false) MultipartFile file) {
        //处理前台传来的图像,做法：1.将图片传入python后台标记处理并保存到本地，然后传回图片地址、图片标记的box类型、每个类型个数、以及查询到的推荐产品到前台显示
        //存储图像到minio服务器
        try {
            //创建一个MinIO的Java客户端
            MinioClient minioClient =MinioClient.builder()
                    .endpoint(ENDPOINT)
                    .credentials(ACCESS_KEY,SECRET_KEY)
                    .build();
            boolean isExist = minioClient.bucketExists(BucketExistsArgs.builder().bucket(BUCKET_NAME).build());
            if (isExist) {
                LOGGER.info("存储桶已经存在！");
            } else {
                //创建存储桶并设置只读权限
                minioClient.makeBucket(MakeBucketArgs.builder().bucket(BUCKET_NAME).build());
                BucketPolicyConfigDto bucketPolicyConfigDto = createBucketPolicyConfigDto(BUCKET_NAME);
                SetBucketPolicyArgs setBucketPolicyArgs = SetBucketPolicyArgs.builder()
                        .bucket(BUCKET_NAME)
                        .config(JSONUtil.toJsonStr(bucketPolicyConfigDto))
                        .build();
                minioClient.setBucketPolicy(setBucketPolicyArgs);
            }
            String filename = file.getOriginalFilename();
            // 设置存储对象名称
            String objectName = "img_process" + "/" + filename;
            // 使用putObject上传一个文件到存储桶中
            PutObjectArgs putObjectArgs = PutObjectArgs.builder()
                    .bucket(BUCKET_NAME)
                    .object(objectName)
                    .contentType(file.getContentType())
                    .stream(file.getInputStream(), file.getSize(), ObjectWriteArgs.MIN_MULTIPART_SIZE).build();
            minioClient.putObject(putObjectArgs);
            LOGGER.info("文件上传成功!");
            ImgProcessDto imgProcessDto = new ImgProcessDto();
            imgProcessDto.setName(filename);
            imgProcessDto.setUrl(ENDPOINT + "/" + BUCKET_NAME + "/" + objectName);
            //文件上传成功，图片标记、特征提取，传回前台
            return CommonResult.success(imgProcessDto);
        } catch (Exception e) {
            e.printStackTrace();
            LOGGER.info("上传发生错误: {}！", e.getMessage());
        }
        return CommonResult.failed();
    }
    private BucketPolicyConfigDto createBucketPolicyConfigDto(String bucketName) {
        BucketPolicyConfigDto.Statement statement = BucketPolicyConfigDto.Statement.builder()
                .Effect("Allow")
                .Principal("*")
                .Action("s3:GetObject")
                .Resource("arn:aws:s3:::"+bucketName+"/*.**").build();
        return BucketPolicyConfigDto.builder()
                .Version("2012-10-17")
                .Statement(CollUtil.toList(statement))
                .build();
    }

    @ApiOperation("推荐")
    @RequestMapping(value = "/img_pro", method = RequestMethod.GET)
    @ResponseBody
    public CommonResult imgPro(@RequestParam(required = false) Map<String, String> img_hash) {

        HomeContentResult result = null;
        List<PmsProduct> resultList = new ArrayList<>();
        for (Map.Entry<String, String> entry : img_hash.entrySet()) {
            //逐一处理每一种推荐
            result = portalProductService.searchRecommendation(entry.getKey());
            if(result != null && entry.getValue()!= ""){
                List<PmsProduct> productList = result.getNewProductList();
                //计算相似度
                for (PmsProduct product : productList){
                    try {

                        String[] args = new String[] { "python", "D:\\ProgramData\\YOLO-V3-Tensorflow-dev\\YOLO-V3-Tensorflow-dev\\img_toHash.py", entry.getValue(), product.getProductFeature() };

                        Process proc = Runtime.getRuntime().exec(args);// 执行py文件

                        BufferedReader in = new BufferedReader(new InputStreamReader(proc.getInputStream()));

                        String line = null;
                        while ((line = in.readLine()) != null) {
                            System.out.println(line);
                            product.setProductSimilarity(line);
                        }
                        in.close();
                        proc.waitFor();
                    } catch (IOException e) {
                        e.printStackTrace();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }

                //排序
                Collections.sort(productList, new Comparator<PmsProduct>() {
                    @Override
                    public int compare(PmsProduct o1, PmsProduct o2) {
                        Double diff = Double.valueOf(o1.getProductSimilarity()) - Double.valueOf(o2.getProductSimilarity());
                        if (diff > 0) {
                            return -1;
                        } else if (diff < 0) {
                            return 1;
                        }
                        return 0; //相等为0
                    }
                });

                //保留前三个
                if(productList.size() > 0){
                    resultList.add(productList.get(0));
                }
                if(productList.size() > 1){
                    resultList.add(productList.get(1));
                }
                if(productList.size() > 2){
                    resultList.add(productList.get(2));
                }
            }

            System.out.println("Key = " + entry.getKey() + ", Value = " + entry.getValue());

        }
        return CommonResult.success(resultList);
    }

    public int getDistance(String str1, String str2) {
        int distance;
        if (str1.length() != str2.length()) {
            distance = -1;
        } else {
            distance = 0;
            for (int i = 0; i < str1.length(); i++) {
                if (str1.charAt(i) != str2.charAt(i)) {
                    distance++;
                }
            }
        }
        return distance;
    }
    /**
     * calculate Hamming weight for binary number
     * @author
     * @param i the binary number
     * @return Hamming weight of the binary number
     */
    public int getWeight(int i) {
        int n;
        for (n = 0; i > 0; n++) {
            i &= (i - 1);
        }
        return n;
    }
}
