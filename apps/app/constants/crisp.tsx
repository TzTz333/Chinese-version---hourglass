import useUser from "hooks/use-user"; // 从hooks目录导入useUser自定义Hook
import { useCallback, useEffect } from "react"; // 导入React的useCallback和useEffect钩子

// 声明全局变量类型，扩展window对象
declare global {
  interface Window {
    $crisp: any; // crisp聊天平台的全局变量
    CRISP_WEBSITE_ID: any; // crisp网站的ID
  }
}

// Crisp组件
const Crisp = () => {
  const { user } = useUser(); // 使用useUser Hook获取用户信息

  // 使用useCallback Hook创建一个验证当前用户的函数
  const validateCurrentUser = useCallback(() => {
    const currentUser = user ? user : null; // 如果user存在则使用user，否则为null

    if (currentUser && currentUser.email) return currentUser.email; // 如果当前用户存在且有email，则返回email

    return null; // 否则返回null
  }, [user]); // 依赖列表中包含user，当user变化时重新创建这个函数

  // 使用useEffect Hook在组件加载后执行
  useEffect(() => {
    // 如果window对象存在且有有效的当前用户
    if (typeof window && validateCurrentUser()) {
      window.$crisp = []; // 初始化$crisp为一个空数组
      window.CRISP_WEBSITE_ID = process.env.NEXT_PUBLIC_CRISP_ID; // 设置CRISP网站ID为环境变量中的值
      (function () {
        var d = document; // 文档对象
        var s = d.createElement("script"); // 创建script标签
        s.src = "https://client.crisp.chat/l.js"; // 设置script的源为Crisp聊天客户端脚本
        s.async = true; // 设置script为异步加载
        d.getElementsByTagName("head")[0].appendChild(s); // 将script标签添加到文档的head中
        // 如果用户已登录，定义email
        if (validateCurrentUser()) {
          window.$crisp.push(["set", "user:email", [validateCurrentUser()]]); // 设置用户的email
          window.$crisp.push(["do", "chat:hide"]); // 隐藏聊天窗口
          window.$crisp.push(["do", "chat:close"]); // 关闭聊天窗口
        }
      })();
    }
  }, [validateCurrentUser]); // 依赖列表中包含validateCurrentUser，当它变化时重新执行这个effect

  return <></>; // 组件不渲染任何内容
};
export default Crisp; // 默认导出Crisp组件