package com.macro.mall.portal;

import com.macro.mall.portal.controller.PmsPortalProductController;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.python.core.PyFunction;
import org.python.core.PyInteger;
import org.python.core.PyObject;
import org.python.core.PyString;
import org.python.util.PythonInterpreter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;

@RunWith(SpringRunner.class)
@SpringBootTest
public class MallPortalApplicationTests {

    @Autowired
    PmsPortalProductController pmsPortalProductController;

    @Test
    public void contextLoads() {
    }

    @Test
    public void test() {
//        // TODO Auto-generated method stub
//        PythonInterpreter interpreter = new PythonInterpreter();
//        interpreter.execfile("F:\\gradudated\\tools\\Python-Image-feature-extraction-master\\纹理特征\\GLCM\\test.py");
//
//        // 第一个参数为期望获得的函数（变量）的名字，第二个参数为期望返回的对象类型
//        PyFunction pyFunction = interpreter.get("stringToHash", PyFunction.class);
//        String file = "F:\\gradudated/taobao_img\\Imgs_TCD/01951.jpg";
//        //调用函数，如果函数需要参数，在Java中必须先将参数转化为对应的“Python类型”
//        PyObject pyobj = pyFunction.__call__(new PyString(file));
//        System.out.println("the anwser is: " + pyobj);
        long i = Long.valueOf("e142c2556e974e",16);
        System.out.println(i);

    }

}
