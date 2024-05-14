import React, { useCallback, useState } from "react";

import { useRouter } from "next/router";
import Image from "next/image";

// hooks
import useUser from "hooks/use-user";
import useToast from "hooks/use-toast";

// services
import authenticationService from "services/authentication.service";
// layouts
import DefaultLayout from "layouts/default-layout";
// social button
import {
  GoogleLoginButton,
  GithubLoginButton,
  EmailSignInForm,
  EmailPasswordForm,
} from "components/account";
// ui
import { Spinner } from "components/ui";
// icons
import Logo from "public/logo.png";
// types
import type { NextPage } from "next";
/**
 * Sign In 页面组件
 */
const SignInPage: NextPage = () => {
  // router
  const router = useRouter();
  // user hook
  const { mutateUser } = useUser();
  // states
  const [isLoading, setLoading] = useState(false);

  const { setToastAlert } = useToast();

  /**
   * 当登录成功时的回调函数
   */
  const onSignInSuccess = useCallback(async () => {

    console.log("onSignInSuccess!!!");
    setLoading(true);
    console.log("hhhhhhhh");

    await mutateUser();
    console.log("mutateUser");
    console.log("router",router);

    const nextLocation = router.asPath.split("?next=")[1];

    if (nextLocation) await router.push(nextLocation as string);
    else {
      console.log("router.push");
      await router.push("/");
      console.log("router.push!!!!", router);
    }
  }, [mutateUser, router]);


  /**
   * 处理 Google 登录
   * @param clientId - Google 客户端 ID
   * @param credential - Google 登录凭证
   */
  const handleGoogleSignIn = ({ clientId, credential }: any) => {
    if (clientId && credential) {
      setLoading(true);
      authenticationService
        .socialAuth({
          medium: "google",
          credential,
          clientId,
        })
        .then(async () => {
          await onSignInSuccess();
        })
        .catch((err) => {
          console.log(err);
          setToastAlert({
            title: "Error signing in!",
            type: "error",
            message: "Something went wrong. Please try again later or contact the support team.",
          });
          setLoading(false);
        });
    }
  };

  /**
   * 处理 Github 登录
   * @param credential - Github 登录凭证
   */
  const handleGithubSignIn = useCallback(
    (credential: string) => {
      setLoading(true);
      authenticationService
        .socialAuth({
          medium: "github",
          credential,
          clientId: process.env.NEXT_PUBLIC_GITHUB_ID,
        })
        .then(async () => {
          await onSignInSuccess();
        })
        .catch((err) => {
          console.log(err);
          setToastAlert({
            title: "Error signing in!",
            type: "error",
            message: "Something went wrong. Please try again later or contact the support team.",
          });
          setLoading(false);
        });
    },
    [onSignInSuccess, setToastAlert]
  );

  return (
    <DefaultLayout
      meta={{
        title: "Plane - Sign In",
      }}
    >
      {isLoading && (
        <div className="absolute top-0 left-0 z-50 flex h-full w-full flex-col items-center justify-center gap-y-3 bg-white">
          <h2 className="text-2xl text-gray-900">登录中 请等待...</h2>
          <Spinner />
        </div>
      )}
      <div className="flex h-screen w-full items-center justify-center overflow-auto bg-gray-50">
        <div className="flex min-h-full w-full flex-col justify-center py-12 px-6 lg:px-8">
          <div className="flex flex-col gap-10 sm:mx-auto sm:w-full sm:max-w-md">
            <div className="flex flex-col items-center justify-center gap-10">
              <Image src={Logo} height={80} width={80} alt="Plane Web Logo" />
              <h2 className="text-center text-xl font-medium text-black">
                登录您的账户
              </h2>
            </div>

            <div className="flex flex-col rounded-[10px] bg-white  shadow-md">
              {parseInt(process.env.NEXT_PUBLIC_ENABLE_OAUTH || "0") ? (
                <>
                  <EmailSignInForm handleSuccess={onSignInSuccess} />

                  <div className="flex flex-col gap-3 py-5 px-5 border-t items-center justify-center border-gray-300 ">
                    <GoogleLoginButton handleSignIn={handleGoogleSignIn} />

                    <GithubLoginButton handleSignIn={handleGithubSignIn} />
                  </div>
                </>
              ) : (
                <>
                  <EmailPasswordForm onSuccess={onSignInSuccess} />
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </DefaultLayout>
  );
};

export default SignInPage;
