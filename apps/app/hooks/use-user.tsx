import { useContext, useEffect } from "react";
import { useRouter } from "next/router";
// context
import { UserContext } from "contexts/user.context";

interface useUserOptions {
  redirectTo?: string;
}

/**
 * 自定义 Hook：useUser
 *
 * @param options 配置选项
 * @returns 返回用户上下文数据
 */
const useUser = (options: useUserOptions = {}) => {
  // props
  const { redirectTo = null } = options;
  // context
  const contextData = useContext(UserContext);
  // router
  const router = useRouter();

  /**
   * 检查重定向 URL 和从 API 获取的用户详情。
   * 如果用户未经身份验证，则将用户重定向到提供的 redirectTo 路由。
   */
  useEffect(() => {
    console.log("useUser useEffect",contextData);

    if (!contextData?.user || !redirectTo) return;

    if (!contextData?.user) {
      if (redirectTo) {
        router?.pathname !== redirectTo && router.push(redirectTo);
      }
      router?.pathname !== "/signin" && router.push("/signin");
    }
    if (contextData?.user) {
      if (redirectTo) {
        router?.pathname !== redirectTo && router.push(redirectTo);
      }
    }
  }, [contextData?.user, redirectTo, router]);

  console.log("useUser",contextData);

  return { ...contextData };
};

export default useUser;
