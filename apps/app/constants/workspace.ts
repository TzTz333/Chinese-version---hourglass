import Welcome from "public/onboarding/welcome.svg";
import Issue from "public/onboarding/issue.svg";
import Cycle from "public/onboarding/cycle.svg";
import Module from "public/onboarding/module.svg";
import CommandMenu from "public/onboarding/command-menu.svg";

export const ROLE = {
  5: "访客",
  10: "参观者",
  15: "成员",
  20: "管理员",
};

export const COMPANY_SIZE = [
  { value: 5, label: "5" },
  { value: 10, label: "10" },
  { value: 25, label: "25" },
  { value: 50, label: "50" },
];

export const USER_ROLES = [
  { value: "Founder or leadership team", label: "团队领导" },
  // { value: "Product manager", label: "产品经理" },
  // { value: "Designer", label: "设计师" },
  { value: "Software developer", label: "软件开发者" },
  { value: "Freelancer", label: "自由工作者" },
  // { value: "Other", label: "其他" },
];

export const ONBOARDING_CARDS = {
  welcome: {
    imgURL: Welcome,
    step: "1/5",
    title: "欢迎您的使用",
    description: "Plane 帮助您计划您的问题、周期和产品模块，以便更快地发布。",
  },
  issue: {
    imgURL: Issue,
    step: "2/5",
    title: "Issues板块",
    description:
      "issue 是 Plane 的构建块。Plane 中的大多数概念都与问题及其属性相关联。",
  },
  cycle: {
    imgURL: Cycle,
    step: "3/5",
    title: "Cycles板块",
    description:
      "Cycles 帮助您和您的团队更快地进步，类似于敏捷开发中常用的冲刺。",
  },
  module: {
    imgURL: Module,
    step: "4/5",
    title: "Break into Modules ",
    description:
      "Modules 将您的大思想分解为项目或功能，以帮助您更好地组织。",
  },
  commandMenu: {
    imgURL: CommandMenu,
    step: "5 /5",
    title: "Command Menu",
    description: "使用命令菜单，您可以在平台上创建、更新和导航。",
  },
};
