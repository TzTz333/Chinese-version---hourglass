// 导入 Next.js 的 Link 组件和 useRouter 钩子
import Link from "next/link";
import { useRouter } from "next/router";

// 定义组件接受的 props 类型
type Props = {
  profilePage: boolean; // 标记是否为个人资料页面
};

const SettingsNavbar: React.FC<Props> = ({ profilePage = false }) => {
  const router = useRouter(); // 使用 useRouter 钩子获取路由信息
  const { workspaceSlug, projectId } = router.query; // 从路由查询参数中解构出 workspaceSlug 和 projectId

  // 工作区设置页的链接数组
  const workspaceLinks: Array<{
    label: string;
    href: string;
  }> = [
      // 每个链接对象包含标签名和对应的 href 属性
      {
        label: "通用设置",
        href: `/${workspaceSlug}/settings`,
      },
      {
        label: "成员",
        href: `/${workspaceSlug}/settings/members`,
      },
      // {
      //   label: "Billing & Plans",
      //   href: `/${workspaceSlug}/settings/billing`,
      // },
      // {
      //   label: "Integrations",
      //   href: `/${workspaceSlug}/settings/integrations`,
      // },
      // {
      //   label: "Import/Export",
      //   href: `/${workspaceSlug}/settings/import-export`,
      // },
    ];

  // 项目设置页的链接数组
  const projectLinks: Array<{
    label: string;
    href: string;
  }> = [
      {
        label: "通用设置",
        href: `/${workspaceSlug}/projects/${projectId}/settings`,
      },
      // {
      //   label: "人员设置",
      //   href: `/${workspaceSlug}/projects/${projectId}/settings/control`,
      // },
      {
        label: "成员",
        href: `/${workspaceSlug}/projects/${projectId}/settings/members`,
      },
      // {
      //   label: "Features",
      //   href: `/${workspaceSlug}/projects/${projectId}/settings/features`,
      // },
      // {
      //   label: "States",
      //   href: `/${workspaceSlug}/projects/${projectId}/settings/states`,
      // },
      // {
      //   label: "Labels",
      //   href: `/${workspaceSlug}/projects/${projectId}/settings/labels`,
      // },
      // {
      //   label: "Integrations",
      //   href: `/${workspaceSlug}/projects/${projectId}/settings/integrations`,
      // },
    ];

  // 个人资料页的链接数组
  const profileLinks: Array<{
    label: string;
    href: string;
  }> = [
      {
        label: "基本信息",
        href: `/${workspaceSlug}/me/profile`,
      },
      {
        label: "动态",
        href: `/${workspaceSlug}/me/profile/activity`,
      },
    ];

  return (
    <div className="flex flex-wrap gap-4">
      {/* 根据传入的 profilePage 和 projectId 决定使用哪组链接 */}
      {(profilePage ? profileLinks : projectId ? projectLinks : workspaceLinks).map((link) => (
        <Link key={link.href} href={link.href}>
          <a>
            <div
              className={`rounded-3xl border px-5 py-1.5 text-sm sm:px-7 sm:py-2 sm:text-base ${router.asPath === link.href
                ? "border-theme bg-theme text-white" // 如果当前路径与链接匹配，使用主题色彩样式
                : "border-gray-300 bg-white hover:bg-hover-gray" // 否则使用默认样式，并在悬停时改变背景色
                }`}
            >
              {link.label}
            </div>
          </a>
        </Link>
      ))}
    </div>
  );
};

export default SettingsNavbar;
