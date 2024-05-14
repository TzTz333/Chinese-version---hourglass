//主要用于处理用户认证和重定向逻辑
// cookies
import { convertCookieStringToObject } from "./cookie";
// types
import type { IProjectMember, IUser, IWorkspace, IWorkspaceMember } from "types";

export const requiredAuth = async (cookie?: string) => {
  const cookies = convertCookieStringToObject(cookie);
  const token = cookies?.accessToken;

  if (!token) return null;

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.plane.so";

  let user: IUser | null = null;

  try {
    console.log("request to: /api/users/me/",baseUrl,token);

    const data = await fetch(`${baseUrl}/api/users/me/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => data);

    user = data.user;

    console.log("get responst: /api/users/me/",data);

  } catch (err) {
    console.error(err);
    user = null;
  }

  return user;
};

export const requiredAdmin = async (workspaceSlug: string, projectId: string, cookie?: string) => {
  const user = await requiredAuth(cookie);

  if (!user) return null;

  const cookies = convertCookieStringToObject(cookie);
  const token = cookies?.accessToken;

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.plane.so";

  let memberDetail: IProjectMember | null = null;

  try {
    const data = await fetch(
      `${baseUrl}/api/workspaces/${workspaceSlug}/projects/${projectId}/project-members/me/`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )
      .then((res) => res.json())
      .then((data) => data);

    memberDetail = data;
  } catch (err) {
    console.error(err);
    memberDetail = null;
  }

  return memberDetail || null;
};

export const requiredWorkspaceAdmin = async (workspaceSlug: string, cookie?: string) => {
  const user = await requiredAuth(cookie);

  if (!user) return null;

  const cookies = convertCookieStringToObject(cookie);
  const token = cookies?.accessToken;

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.plane.so";

  let memberDetail: IWorkspaceMember | null = null;

  try {
    const data = await fetch(`${baseUrl}/api/workspaces/${workspaceSlug}/workspace-members/me/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => data);

    memberDetail = data;
  } catch (err) {
    console.error(err);
    memberDetail = null;
  }

  return memberDetail || null;
};

export const homePageRedirect = async (cookie?: string) => {
  const user = await requiredAuth(cookie);

  if (!user)
    return {
      redirect: {
        destination: "/signin",
        permanent: false,
      },
    };

//修复:后端返回用户和工作空间的对象。
//如果需要发送用户和工作空间，获取KT
//是，修改如下
  if (!user.is_onboarded)
    return {
      redirect: {
        destination: "/onboarding",
        permanent: false,
      },
    };

  let workspaces: IWorkspace[] = [];

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.plane.so";

  const cookies = convertCookieStringToObject(cookie);
  const token = cookies?.accessToken;

  //获取用户的工作空间
  try {
    const data = await fetch(`${baseUrl}/api/users/me/workspaces/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => data);

    workspaces = data;
  } catch (e) {
    console.error(e);
    return {
      redirect: {
        destination: "/error",
        permanent: false,
      },
    };
  }

  //获取用户最后活跃的工作空间，如果有，跳转到该工作空间，如果没有，跳转到第一个工作空间
  const lastActiveWorkspace = workspaces.find(
    (workspace) => workspace.id === user.last_workspace_id
  );

  if (lastActiveWorkspace) {
    return {
      redirect: {
        destination: `/${lastActiveWorkspace.slug}`,
        permanent: false,
      },
    };
  } else if (workspaces.length > 0) {
    return {
      redirect: {
        destination: `/${workspaces[0].slug}`,
        permanent: false,
      },
    };
  }

  //如果用户没有工作空间，跳转到创建工作空间页面，如果有，跳转到第一个工作空间
  const invitations = await fetch(`${baseUrl}/api/users/me/invitations/workspaces/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  })
    .then((res) => res.json())
    .then((data) => data)
    .catch((e) => {
      console.error(e);
      return {
        redirect: {
          destination: "/error",
          permanent: false,
        },
      };
    });

  if (invitations.length > 0)
    return {
      redirect: {
        destination: "/invitations",
        permanent: false,
      },
    };
  else {
    return {
      redirect: {
        destination: "/create-workspace",
        permanent: false,
      },
    };
  }
};
