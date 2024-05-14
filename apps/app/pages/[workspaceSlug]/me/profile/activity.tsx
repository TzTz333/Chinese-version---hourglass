// 导入 Next.js 的服务器端属性类型
import { GetServerSidePropsContext } from "next";

// 导入 SWR 库，用于数据获取和缓存管理
import useSWR from "swr";

// 导入服务，这里是 userService，提供用户相关的 API 调用
import userService from "services/user.service";
// 导入认证函数，用于服务器端检查用户登录状态
import { requiredAuth } from "lib/auth";
// 导入应用布局组件
import AppLayout from "layouts/app-layout";
// 导入 UI 组件，Loader 用于显示加载动画
import { Loader } from "components/ui";
// 导入面包屑导航组件
import { BreadcrumbItem, Breadcrumbs } from "components/breadcrumbs";
// 导入 Feeds 组件，用于显示用户活动列表
import { Feeds } from "components/core";
// 导入常量，这里是用户活动的 fetch key
import { USER_ACTIVITY } from "constants/fetch-keys";

const ProfileActivity = () => {
  // 使用 SWR 钩子获取用户活动数据，key 为 USER_ACTIVITY，fetcher 函数通过 userService 调用 API 获取数据
  const { data: userActivity } = useSWR(USER_ACTIVITY, () => userService.getUserActivity());

  return (
    // 应用布局组件包裹页面内容，设置页面元数据和提示导航
    <AppLayout
      meta={{
        title: "Plane - My Profile", // 页面标题
      }}
      breadcrumbs={
        <Breadcrumbs>
          <BreadcrumbItem title="我的活动记录" />
        </Breadcrumbs>
      }
      settingsLayout // 表示在设置布局中显示此页面内容
      profilePage  // 表示这是个人资料页的一部分
    >
      {/* 根据 userActivity 数据存在与否渲染不同的 UI */}
      {userActivity ? (
        userActivity.results.length > 0 ? (
          <Feeds activities={userActivity.results} />
        ) : null
       ) : (
        <Loader className="space-y-5">
          {/* 在等待数据时显示加载占位符 */}
          <Loader.Item height="40px" />
          <Loader.Item height="40px" />
          <Loader.Item height="40px" />
          <Loader.Item height="40px" />
        </Loader>
      )}
    </AppLayout>
  );
};

export const getServerSideProps = async (ctx: GetServerSidePropsContext) => {
  // 在服务器端执行认证检查。如果未认证，则重定向到登录页面。
  const user = await requiredAuth(ctx.req?.headers.cookie);

  const redirectAfterSignIn = ctx.resolvedUrl;

  if (!user) {
    return {
      redirect: {
        destination: `/signin?next=${redirectAfterSignIn}`,// 登录后的重定向地址为当前页
        permanent: false,
      },
    };
  }

  return {
    props: {
      user, // 将用户信息作为 props 传递给组件
    },
  };
};

export default ProfileActivity;
