// lib
import { homePageRedirect } from "lib/auth";
// types
import type { NextPage, NextPageContext } from "next";

//定义Home组件，返回null
const Home: NextPage = () => null;

//定义getServerSideProps方法，传入ctx参数，
//返回homePageRedirect(cookies)，其中cookies为ctx.req?.headers.cookie
export const getServerSideProps = (ctx: NextPageContext) => {
  const cookies = ctx.req?.headers.cookie;
  return homePageRedirect(cookies);
};

export default Home;
