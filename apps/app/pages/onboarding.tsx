import { useState } from "react";

import Image from "next/image";
import { useRouter } from "next/router";

// lib
import { requiredAuth } from "lib/auth"; // 导入身份验证库
// services
import userService from "services/user.service"; // 导入用户服务
// hooks
import useUser from "hooks/use-user"; // 导入用户钩子
// layouts
import DefaultLayout from "layouts/default-layout"; // 导入默认布局
// components
import { InviteMembers, OnboardingCard, UserDetails, Workspace } from "components/onboarding"; // 导入入职相关组件
// ui
import { PrimaryButton } from "components/ui"; // 导入UI组件
// constant
import { ONBOARDING_CARDS } from "constants/workspace"; // 导入常量
// images
import Logo from "public/onboarding/logo.svg"; // 导入Logo图片
// types
import type { NextPage, GetServerSidePropsContext } from "next"; // 导入Next.js类型

/**
* 登录页面组件。
* 为新用户呈现入职流程。
 */
const Onboarding: NextPage = () => {
  const [step, setStep] = useState(1); // 记录入职流程的步骤
  const [userRole, setUserRole] = useState<string | null>(null); // 记录用户角色

  const [workspace, setWorkspace] = useState(); // 记录工作区信息

  const router = useRouter(); // 使用Next.js路由器

  const { user } = useUser(); // 使用自定义钩子获取用户信息

  return (
    <DefaultLayout>
      <div className="grid h-full place-items-center p-5">
        {step <= 3 ? (
          <div className="w-full">
            {/* 根据步骤显示对应组件 */}
            <div className="text-center mb-8">
              <Image src={Logo} height="50" alt="Plane Logo" />
            </div>
            {step === 1 ? (
              <UserDetails user={user} setStep={setStep} setUserRole={setUserRole} />
            ) : step === 2 ? (
              <Workspace setStep={setStep} setWorkspace={setWorkspace} />
            ) : (
              <InviteMembers setStep={setStep} workspace={workspace} />
            )}
          </div>
        ) : (
          <div className="flex w-full max-w-2xl flex-col gap-12">
            <div className="flex flex-col items-center justify-center gap-7 rounded-[10px] bg-white px-14 py-10 text-center shadow-md">
              {/* 显示入职卡片 */}
              {step === 4 ? (
                <OnboardingCard data={ONBOARDING_CARDS.welcome} />
              ) : step === 5 ? (
                <OnboardingCard data={ONBOARDING_CARDS.issue} />
              ) : step === 6 ? (
                <OnboardingCard data={ONBOARDING_CARDS.cycle} />
              ) : step === 7 ? (
                <OnboardingCard data={ONBOARDING_CARDS.module} />
              ) : (
                <OnboardingCard data={ONBOARDING_CARDS.commandMenu} />
              )}
              {/* // 显示按钮并处理点击事件 */}
              <div className="mx-auto flex h-1/4 items-end lg:w-1/2">
                <PrimaryButton
                  type="button"
                  className="flex w-full items-center justify-center text-center "
                  size="md"
                  onClick={() => {
                    if (step === 8) {
                      userService
                        .updateUserOnBoard({ userRole })
                        .then(() => {
                          router.push("/");
                        })
                        .catch((err) => {
                          console.log(err);
                        });
                    } else setStep((prevData) => prevData + 1);
                  }}
                >
                  {step === 4 || step === 8 ? "开始" : "下一步"}
                </PrimaryButton>
              </div>
            </div>
          </div>
        )}
      </div>
    </DefaultLayout>
  );
};

// 服务器端渲染入口函数
export const getServerSideProps = async (ctx: GetServerSidePropsContext) => {
  const user = await requiredAuth(ctx.req?.headers.cookie); // 检查用户认证

  const redirectAfterSignIn = ctx.resolvedUrl; // 登录后重定向的URL

  if (!user) {
    return {
      redirect: {
        destination: `/signin?next=${redirectAfterSignIn}`,
        permanent: false,
      },
    };
  }

  return {
    props: {
      user,
    },
  };
};

export default Onboarding;
