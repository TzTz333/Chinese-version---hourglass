// 引入 React 钩子和上下文 API
import { createContext, useCallback, useReducer, useEffect } from "react";
// 引入 Next.js 的路由钩子
import { useRouter } from "next/router";
// 引入 SWR 库用于数据获取和状态管理
import useSWR from "swr";

// 引入组件
import ToastAlert from "components/toast-alert";
// 引入服务层，用于与后端 API 交互
import projectService from "services/project.service";
// 引入常量，用于定义 fetch 键
import { USER_PROJECT_VIEW } from "constants/fetch-keys";

// 创建一个新的上下文，用于在组件间共享主题状态
export const themeContext = createContext<ContextType>({} as ContextType);

// 定义主题属性类型
type ThemeProps = {
  collapsed: boolean;// 侧边栏是否折叠
};

// 定义 action 类型
type ReducerActionType = {
  type: "TOGGLE_SIDEBAR" | "REHYDRATE_THEME";// 切换侧边栏状态或重新加载主题
  payload?: Partial<ThemeProps>;
};

// 定义上下文类型
type ContextType = {
  collapsed: boolean; // 侧边栏是否折叠
  toggleCollapsed: () => void; // 切换侧边栏状态的函数
};

// 定义状态类型
type StateType = {
  collapsed: boolean;// 侧边栏是否折叠
};
// 定义 reducer 函数类型
type ReducerFunctionType = (state: StateType, action: ReducerActionType) => StateType;

// 定义初始状态
export const initialState: StateType = {
  collapsed: false,// 默认不折叠
};

// 定义处理状态变更的 reducer 函数
export const reducer: ReducerFunctionType = (state, action) => {
  const { type, payload } = action;

  switch (type) {
    case "TOGGLE_SIDEBAR":
      // 切换侧边栏的展开/折叠状态
      const newState = {
        ...state,
        collapsed: !state.collapsed,
      };
      // 将新状态保存到 localStorage，以便下次加载时使用
      localStorage.setItem("collapsed", JSON.stringify(newState.collapsed));
      return newState;

    case "REHYDRATE_THEME": {
      // 从 localStorage 重新加载侧边栏状态
      let collapsed: any = localStorage.getItem("collapsed");
      collapsed = collapsed ? JSON.parse(collapsed) : false;
      return { ...initialState, ...payload, collapsed };
    }

    default: {
      // 默认返回原状态
      return state;
    }
  }
};

// 定义 ThemeContextProvider 组件，用于封装状态管理逻辑和提供上下文
export const ThemeContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 使用 useReducer 管理状态
  const [state, dispatch] = useReducer(reducer, initialState);

  // 使用 useRouter 获取路由信息
  const router = useRouter();
  const { workspaceSlug, projectId } = router.query;

  // 使用 useSWR 获取项目视图配置数据
  const { data: myViewProps } = useSWR(
    workspaceSlug && projectId ? USER_PROJECT_VIEW(projectId as string) : null,
    workspaceSlug && projectId
      ? () => projectService.projectMemberMe(workspaceSlug as string, projectId as string)
      : null
  );

  // 定义回调函数，用于切换侧边栏展开/折叠状态
  const toggleCollapsed = useCallback(() => {
    dispatch({
      type: "TOGGLE_SIDEBAR",
    });
  }, []);

  // 使用 useEffect 根据从服务器获取的数据重新设置组件的状态
  useEffect(() => {
    dispatch({
      type: "REHYDRATE_THEME",
      payload: myViewProps?.view_props as any,
    });
  }, [myViewProps]);

  // 返回 provider 组件，提供上下文给子组件
  return (
    <themeContext.Provider
      value={{
        collapsed: state.collapsed,
        toggleCollapsed,
      }}
    >
      {/* 渲染 ToastAlert 组件用于显示通知 */}
      <ToastAlert />
      {/* 渲染所有子组件 */}
      {children}
    </themeContext.Provider>
  );
};
