// 导入 React 及其相关钩子函数
import React, { useEffect, useState } from "react";

// 导入 Next.js 的 Image 组件，用于优化图片加载
import Image from "next/image";

// 导入 react-hook-form 库，用于表单处理
import { Controller, useForm } from "react-hook-form";
// 导入认证相关的库函数，用于权限验证
import { requiredAuth } from "lib/auth";
// 导入服务层，用于处理文件和用户信息的请求
import fileService from "services/file.service";
import userService from "services/user.service";
// 导入自定义钩子，用于获取用户信息和显示提示信息
import useUser from "hooks/use-user";
import useToast from "hooks/use-toast";
// 导入布局组件，这里是应用的布局组件
import AppLayout from "layouts/app-layout";
// 导入核心组件，这里是图片上传模态框
import { ImageUploadModal } from "components/core";
// 导入 UI 组件，包括选择器、按钮、输入框、加载动画等
import { CustomSelect, DangerButton, Input, SecondaryButton, Spinner } from "components/ui";
// 导入面包屑导航相关组件
import { BreadcrumbItem, Breadcrumbs } from "components/breadcrumbs";
// 导入图标组件
import { UserIcon } from "@heroicons/react/24/outline";
// 导入类型定义和 Next.js 特定类型
import type { NextPage, GetServerSidePropsContext } from "next";
import type { IUser } from "types";
// 导入常量，这里是用户角色常量定义
import { USER_ROLES } from "constants/workspace";

const defaultValues: Partial<IUser> = {
  avatar: "",
  first_name: "",
  last_name: "",
  email: "",
  role: "",
};

const Profile: NextPage = () => {
  // 定义状态管理变量：编辑状态、删除状态、图片上传模态框开关状态等
  const [isEditing, setIsEditing] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  const [isImageUploadModalOpen, setIsImageUploadModalOpen] = useState(false);

  // 使用 useForm 钩子初始化表单并设置默认值与规则等
  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    control,
    formState: { errors, isSubmitting },
  } = useForm<IUser>({ defaultValues });

  // 使用自定义 hook 获取用户信息和设置 Toast 提醒信息
  const { setToastAlert } = useToast();
  const { user: myProfile, mutateUser } = useUser();

  // 使用 useEffect 钩子在用户信息更新时重置表单值
  useEffect(() => {
    reset({ ...defaultValues, ...myProfile });
  }, [myProfile, reset]);

  // 定义表单提交逻辑，异步提交用户信息更改请求，并处理响应结果
  const onSubmit = async (formData: IUser) => {
    const payload: Partial<IUser> = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      avatar: formData.avatar,
      role: formData.role,
    };

    console.log("payload:", payload);

    await userService
      .updateUser(payload)
      .then((res) => {
        mutateUser((prevData) => {
          if (!prevData) return prevData;
          return { ...prevData, user: { ...payload, ...res } };
        }, false);
        setIsEditing(false);
        setToastAlert({
          type: "success",
          title: "Success!",
          message: "Profile updated successfully.",
        });
      })
      .catch(() =>
        setToastAlert({
          type: "error",
          title: "Error!",
          message: "There was some error in updating your profile. Please try again.",
        })
      );
  };

  // 定义删除头像的逻辑。如果 URL 存在，则发送删除请求。
  const handleDelete = (url: string | null | undefined, updateUser: boolean = false) => {
    if (!url) return;

    setIsRemoving(true);

    const index = url.indexOf(".com");
    const asset = url.substring(index + 5);

    fileService.deleteUserFile(asset).then(() => {
      if (updateUser)
        userService
          .updateUser({ avatar: "" })
          .then((res) => {
            setToastAlert({
              type: "success",
              title: "Success!",
              message: "Profile picture removed successfully.",
            });
            mutateUser((prevData) => {
              if (!prevData) return prevData;
              return { ...prevData, user: res };
            }, false);
          })
          .catch(() => {
            setToastAlert({
              type: "error",
              title: "Error!",
              message: "There was some error in deleting your profile picture. Please try again.",
            });
          })
          .finally(() => setIsRemoving(false));
    });
  };

  return (
    <AppLayout
      meta={{
        title: "Plane - My Profile",
      }}
      breadcrumbs={
        <Breadcrumbs>
          <BreadcrumbItem title="我的个人资料" />
        </Breadcrumbs>
      }
      settingsLayout
      profilePage
    >
      <ImageUploadModal
        isOpen={isImageUploadModalOpen}
        onClose={() => setIsImageUploadModalOpen(false)}
        onSuccess={(url) => {
          setValue("avatar", url);
          handleSubmit(onSubmit)();
          setIsImageUploadModalOpen(false);
        }}
        value={watch("avatar") !== "" ? watch("avatar") : undefined}
        userImage
      />
      {myProfile ? (
        <div className="space-y-8 sm:space-y-12">
          <div className="grid grid-cols-12 gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">个人资料设置</h4>
              <p className="text-gray-500">
              最大文件大小为 5MB。支持的文件类型为 .jpg 和 .png
              </p>
            </div>
            <div className="col-span-12 sm:col-span-6">
              <div className="flex items-center gap-4">
                <button type="button" onClick={() => setIsImageUploadModalOpen(true)}>
                  {!watch("avatar") || watch("avatar") === "" ? (
                    <div className="bg-gray-100 h-12 w-12 p-2 rounded-md">
                      <UserIcon className="h-full w-full text-gray-300" />
                    </div>
                  ) : (
                    <div className="relative h-12 w-12 overflow-hidden">
                      <Image
                        src={watch("avatar")}
                        alt={myProfile.first_name}
                        layout="fill"
                        objectFit="cover"
                        className="rounded-md"
                        onClick={() => setIsImageUploadModalOpen(true)}
                        priority
                      />
                    </div>
                  )}
                </button>
                <div className="flex items-center gap-2">
                  <SecondaryButton
                    onClick={() => {
                      setIsImageUploadModalOpen(true);
                    }}
                  >
                    Upload
                  </SecondaryButton>
                  {myProfile.avatar && myProfile.avatar !== "" && (
                    <DangerButton
                      onClick={() => handleDelete(myProfile.avatar, true)}
                      loading={isRemoving}
                    >
                      {isRemoving ? "Removing..." : "Remove"}
                    </DangerButton>
                  )}
                </div>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-12 gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">昵称</h4>
              <p className="text-gray-500">
               此名称将在你正在处理的所有项目中显示
              </p>
            </div>
            <div className="col-span-12 sm:col-span-6 flex items-center gap-2">
              <Input
                name="first_name"
                id="first_name"
                register={register}
                error={errors.first_name}
                placeholder="Enter your first name"
                autoComplete="off"
                validations={{
                  required: "This field is required.",
                }}
              />
              <Input
                name="last_name"
                register={register}
                error={errors.last_name}
                id="last_name"
                placeholder="Enter your last name"
                autoComplete="off"
              />
            </div>
          </div>
          <div className="grid grid-cols-12 gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">Email</h4>
              <p className="text-gray-500">正在使用的电子邮件地址</p>
            </div>
            <div className="col-span-12 sm:col-span-6">
              <Input
                id="email"
                name="email"
                autoComplete="off"
                register={register}
                error={errors.name}
                className="w-full"
                disabled
              />
            </div>
          </div>
          <div className="grid grid-cols-12 gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">角色</h4>
              <p className="text-gray-500">添加你的角色</p>
            </div>
            <div className="col-span-12 sm:col-span-6">
              <Controller
                name="role"
                control={control}
                rules={{ required: "This field is required" }}
                render={({ field: { value, onChange } }) => (
                  <CustomSelect
                    value={value}
                    onChange={onChange}
                    label={value ? value.toString() : "选择你的角色"}
                    width="w-full"
                    input
                    position="right"
                  >
                    {USER_ROLES.map((item) => (
                      <CustomSelect.Option key={item.value} value={item.value}>
                        {item.label}
                      </CustomSelect.Option>
                    ))}
                  </CustomSelect>
                )}
              />
            </div>
          </div>
          <div className="sm:text-right">
            <SecondaryButton onClick={handleSubmit(onSubmit)} loading={isSubmitting}>
              {isSubmitting ? "Updating..." : "Update profile"}
            </SecondaryButton>
          </div>
        </div>
      ) : (
        <div className="grid h-full w-full place-items-center px-4 sm:px-0">
          <Spinner />
        </div>
      )}
    </AppLayout>
  );
};

export const getServerSideProps = async (ctx: GetServerSidePropsContext) => {
  const user = await requiredAuth(ctx.req?.headers.cookie);

  const redirectAfterSignIn = ctx.resolvedUrl;

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

export default Profile;
