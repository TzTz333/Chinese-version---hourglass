// services
import APIService from "services/api.service";

const { NEXT_PUBLIC_API_BASE_URL } = process.env;

interface UnSplashImage {
  id: string;
  created_at: Date;
  updated_at: Date;
  promoted_at: Date;
  width: number;
  height: number;
  color: string;
  blur_hash: string;
  description: null;
  alt_description: string;
  urls: UnSplashImageUrls;
  [key: string]: any;
}

interface UnSplashImageUrls {
  raw: string;
  full: string;
  regular: string;
  small: string;
  thumb: string;
  small_s3: string;
}

class FileServices extends APIService {
  constructor() {
    super(NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000");
  }

  async uploadFile(workspaceSlug: string, file: FormData): Promise<any> {
    return this.mediaUpload(`/api/workspaces/${workspaceSlug}/file-assets/`, file)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteFile(asset: string): Promise<any> {
    return this.delete(`/api/workspaces/file-assets/${asset}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async uploadUserFile(file: FormData): Promise<any> {
    return this.mediaUpload(`/api/users/file-assets/`, file)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteUserFile(asset: string): Promise<any> {
    return this.delete(`/api/users/file-assets/${asset}`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getUnsplashImages(page: number = 1, query?: string): Promise<UnSplashImage[]> {
    const url = "/api/unsplash";

    return this.request({
      method: "get",
      url,
      params: {
        page,
        per_page: 20,
        query,
      },
    })
      .then((response) => response?.data?.results) //记录一个错误
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}

export default new FileServices();
