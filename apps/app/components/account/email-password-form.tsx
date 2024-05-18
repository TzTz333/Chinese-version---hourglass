// 导入 React 库
import React from "react";

// 导入 Next.js 的 Link 组件，用于客户端导航
import Link from "next/link";

// 导入 react-hook-form 库的 useForm 钩子，用于表单处理
import { useForm } from "react-hook-form";
// 导入认证服务，这里假设是一个处理登录逻辑的服务模块
import authenticationService from "services/authentication.service";
// 导入自定义的 Toast 提示钩子，用于显示提示消息
import useToast from "hooks/use-toast";
// 导入 UI 组件，这里包括输入框（Input）和次级按钮（SecondaryButton）
import { Input, SecondaryButton } from "components/ui";

// 定义表单值类型
type EmailPasswordFormValues = {
  email: string;
  password?: string;
  medium?: string;
};

export const EmailPasswordForm = ({ onSuccess }: any) => {
  // 使用 useToast 钩子获取设置 Toast 提示的方法
  const { setToastAlert } = useToast();
  // 使用 useForm 钩子初始化表单
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting, isValid, isDirty },
  } = useForm<EmailPasswordFormValues>({
    defaultValues: {
      email: "",
      password: "",
      medium: "email",
    },
    mode: "onChange", // 表单验证模式为“onChange”，即字段内容改变时进行验证
    reValidateMode: "onChange",
  });

  // 提交表单时触发的函数
  const onSubmit = (formData: EmailPasswordFormValues) => {
    authenticationService
      .emailLogin(formData) // 调用认证服务进行登录操作
      .then((response) => {
        onSuccess(response); // 登录成功时调用 onSuccess 回调函数
      })
      .catch((error) => {
        console.log(error);
        // 登录失败时显示错误提示信息
        setToastAlert({
          title: "错误！",
          type: "error",
          message: "请输入正确的电子邮件地址和密码进行登录！",
        });
        if (!error?.response?.data) return;
        // 将后端返回的错误信息设置到对应字段上
        Object.keys(error.response.data).forEach((key) => {
          const err = error.response.data[key];
          console.log("err", err);
          setError(key as keyof EmailPasswordFormValues, {
            type: "manual",
            message: Array.isArray(err) ? err.join(", ") : err,
          });
        });
      });
  };

  return (
    <>
      <form className="mt-5 py-5 px-5" onSubmit={handleSubmit(onSubmit)}>
        {/* 邮箱输入框 */}
        <div>
          <Input
            id="email"
            type="email"
            name="email"
            register={register}
            validations={{
              required: "邮箱是必填项！", // 验证规则：必填项和邮箱格式验证
              validate: (value) =>
                /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
                  value
                ) || "邮箱格式不正确！",
            }}
            error={errors.email}
            placeholder="填写邮箱"
          />
        </div>

        {/* 密码输入框 */}
        <div className="mt-5">
          <Input
            id="password"
            type="password"
            name="password"
            register={register}
            validations={{
              required: "密码是必填项！", // 验证规则：必填项
            }}
            error={errors.password}
            placeholder="填写密码"
          />
        </div>
        {/* 
        忘记密码链接
        <div className="mt-2 flex items-center justify-between">
          <div className="ml-auto text-sm">
            <Link href={"/forgot-password"}>
              <a className="font-medium text-theme hover:text-indigo-500">忘记密码</a>
            </Link>
          </div>
        </div> */}

        {/* 提交按钮 */}
        <div className="mt-5">
          <SecondaryButton
            type="submit"
            className="w-full text-center"
            loading={isSubmitting || (!isValid && isDirty)} // 按钮加载状态控制逻辑
          >
            {isSubmitting ? "登录..." : "登   录"}
          </SecondaryButton>
        </div>
      </form>
    </>
  );
};
