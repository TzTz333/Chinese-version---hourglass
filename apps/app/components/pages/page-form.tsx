import { useEffect } from "react";

import dynamic from "next/dynamic";

// react-hook-form
import { Controller, useForm } from "react-hook-form";
// ui
import { Input, Loader, PrimaryButton, SecondaryButton } from "components/ui";
// types
import { IPage } from "types";

type Props = {
  handleFormSubmit: (values: IPage) => Promise<void>;
  handleClose: () => void;
  status: boolean;
  data?: IPage | null;
};

// rich-text-editor
const RemirrorRichTextEditor = dynamic(() => import("components/rich-text-editor"), {
  ssr: false,
  loading: () => (
    <Loader>
      <Loader.Item height="12rem" width="100%" />
    </Loader>
  ),
});

const defaultValues = {
  name: "",
  description: "",
};

export const PageForm: React.FC<Props> = ({ handleFormSubmit, handleClose, status, data }) => {
  const {
    register,
    formState: { errors, isSubmitting },
    handleSubmit,
    reset,
    control,
    setValue,
  } = useForm<IPage>({
    defaultValues,
  });

  const handleCreateUpdatePage = async (formData: IPage) => {
    await handleFormSubmit(formData);

    reset({
      ...defaultValues,
    });
  };

  useEffect(() => {
    reset({
      ...defaultValues,
      ...data,
    });
  }, [data, reset]);

  return (
    <form onSubmit={handleSubmit(handleCreateUpdatePage)}>
      <div className="space-y-5">
        <h3 className="text-lg font-medium leading-6 text-gray-900">
          {status ? "更新" : "创建"} 文档
        </h3>
        <div className="space-y-3">
          <div>
            <Input
              id="name"
              label="名称"
              name="name"
              type="name"
              placeholder="输入名称"
              autoComplete="off"
              error={errors.name}
              register={register}
              validations={{
                required: "名称是必填项",
                maxLength: {
                  value: 255,
                  message: "名称不得超过25个字",
                },
              }}
            />
          </div>
          {/* <div>
            <Controller
              name="description"
              control={control}
              render={({ field: { value } }) => (
                <RemirrorRichTextEditor
                  value={value}
                  onJSONChange={(jsonValue) => setValue("description", jsonValue)}
                  onHTMLChange={(htmlValue) => setValue("description_html", htmlValue)}
                  placeholder="Description"
                />
              )}
            />
          </div> */}
        </div>
      </div>
      <div className="mt-5 flex justify-end gap-2">
        <SecondaryButton onClick={handleClose}>取消</SecondaryButton>
        <PrimaryButton type="submit" loading={isSubmitting}>
          {status
            ? isSubmitting
              ? "更新文档中..."
              : "更新文档"
            : isSubmitting
              ? "创建文档中..."
              : "创建文档"}
        </PrimaryButton>
      </div>
    </form>
  );
};
