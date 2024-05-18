import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
// 引入UI组件
import { CheckCircleIcon } from "@heroicons/react/20/solid";
import { Input, PrimaryButton, SecondaryButton } from "components/ui";
// 引入服务层
import authenticationService from "services/authentication.service";
import useToast from "hooks/use-toast";
import useTimer from "hooks/use-timer";
// 定义表单字段类型
type EmailCodeFormValues = {
  email: string;
  key?: string;
  token?: string;
};

// 邮件验证码表单组件
export const EmailCodeForm = ({ onSuccess }: any) => {
  // 状态管理
  const [codeSent, setCodeSent] = useState(false); // 是否已发送验证码
  const [codeResent, setCodeResent] = useState(false); // 是否已重新发送验证码
  const [isCodeResending, setIsCodeResending] = useState(false); // 是否正在重新发送验证码
  const [errorResendingCode, setErrorResendingCode] = useState(false); // 重新发送验证码时是否出错

  // 使用自定义Toast和Timer钩子
  const { setToastAlert } = useToast();
  const { timer: resendCodeTimer, setTimer: setResendCodeTimer } = useTimer();

  // 使用react-hook-form库管理表单
  const {
    register,
    handleSubmit,
    setError,
    setValue,
    getValues,
    formState: { errors, isSubmitting, isValid, isDirty },
  } = useForm<EmailCodeFormValues>({
    defaultValues: {
      email: "",
      key: "",
      token: "",
    },
    mode: "onChange", // 表单验证模式：输入字段后立即验证
    reValidateMode: "onChange", // 再次验证模式：输入字段后立即验证
  });

  // 是否禁用再次发送验证码按钮的逻辑
  const isResendDisabled =
    resendCodeTimer > 0 || isCodeResending || isSubmitting || errorResendingCode;

  // 提交表单，发送验证码
  const onSubmit = async ({ email }: EmailCodeFormValues) => {
    setErrorResendingCode(false);
    await authenticationService
      .emailCode({ email })
      .then((res) => {
        setValue("key", res.key);
        setCodeSent(true);
      })
      .catch((err) => {
        setErrorResendingCode(true);
        setToastAlert({
          title: "Oops!",
          type: "error",
          message: err?.error,
        });
      });
  };

  // 处理登录逻辑
  const handleSignin = async (formData: EmailCodeFormValues) => {
    await authenticationService
      .magicSignIn(formData)
      .then((response) => {
        onSuccess(response);
      })
      .catch((error) => {
        setToastAlert({
          title: "Oops!",
          type: "error",
          message: error?.response?.data?.error ?? "Enter the correct code to sign in",
        });
        setError("token" as keyof EmailCodeFormValues, {
          type: "manual",
          message: error.error,
        });
      });
  };

  // 获取当前表单中的email值
  const emailOld = getValues("email");

  // 当email值变化时重置错误状态
  useEffect(() => {
    setErrorResendingCode(false);
  }, [emailOld]);

  // 表单的JSX结构
  return (
    <>
      <form className="space-y-5 py-5 px-5">
        {/* 根据是否发送了验证码或者重新发送了验证码来显示提示消息 */}
        {(codeSent || codeResent) && (
          <div className="rounded-md bg-green-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                {/* 成功图标 */}
                <CheckCircleIcon className="h-5 w-5 text-green-400" aria-hidden="true" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  {codeResent
                    ? "Please check your mail for new code."
                    : "Please check your mail for code."}
                </p>
              </div>
            </div>
          </div>
        )}
        {/* 邮件输入框 */}
        <div>
          <Input
            id="email"
            type="email"
            name="email"
            register={register}
            validations={{
              required: "Email ID is required", // 邮件地址必填
              validate: (value) => // 邮件地址格式验证
                /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
                  value
                ) || "Email ID is not valid",
            }}
            error={errors.email}
            placeholder="Enter your Email ID"
          />
        </div>

        {/* 如果已经发送了验证码，则显示验证码输入框和重新发送验证码按钮 */}
        {codeSent && (
          <div>
            {/* 验证码输入框 */}
            <Input
              id="token"
              type="token"
              name="token"
              register={register}
              validations={{
                required: "Code is required", // 验证码必填
              }}
              error={errors.token}
              placeholder="Enter code"
            />
            {/* 重新发送验证码按钮 */}
            <button
              type="button"
              className={`mt-5 flex w-full justify-end text-xs outline-none ${isResendDisabled ? "cursor-default text-gray-400" : "cursor-pointer text-theme"
                } `}
              onClick={() => {
                setIsCodeResending(true);
                onSubmit({ email: getValues("email") }).then(() => {
                  setCodeResent(true);
                  setIsCodeResending(false);
                  setResendCodeTimer(30); // 重新发送验证码倒计时
                });
              }}
              disabled={isResendDisabled}
            >
              {resendCodeTimer > 0 ? ( // 根据不同状态显示不同文本
                <p className="text-right">
                  Didn{"'"}t receive code? Get new code in {resendCodeTimer} seconds.
                </p>
              ) : isCodeResending ? (
                "Sending code..." // 正在发送验证码
              ) : errorResendingCode ? (
                "Please try again later" // 出错提示
              ) : (
                "Resend code" // 重新发送验证码
              )}
            </button>
          </div>
        )}
        {/* 根据是否发送了验证码来显示不同的按钮 */}
        <div>
          {codeSent ? (
            <PrimaryButton
              type="submit"
              className="w-full text-center"
              size="md"
              onClick={handleSubmit(handleSignin)} // 处理登录
              loading={isSubmitting || (!isValid && isDirty)}
            >
              {isSubmitting ? "Signing in..." : "Sign in"} // 正在登录或登录按钮
            </PrimaryButton>
          ) : (
            <PrimaryButton
              type="submit"
              className="w-full text-center"
              size="md"
              onClick={() => {
                handleSubmit(onSubmit)().then(() => {
                  setResendCodeTimer(30); // 发送验证码倒计时
                });
              }}
              loading={isSubmitting || (!isValid && isDirty)}
            >
              {isSubmitting ? "Sending code..." : "Send code"} // 正在发送验证码或发送验证码按钮
            </PrimaryButton>
          )}
        </div>
      </form>
    </>
  );
};