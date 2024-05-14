// services
import APIService from "services/api.service";

const { NEXT_PUBLIC_API_BASE_URL } = process.env;

//定义AuthService类，继承APIService类，
//用于处理登录、登出、获取用户信息等操作，这里主要是处理登录相关的操作，
//包括邮箱登录、社交登录、邮箱验证码登录、链接登录等
class AuthService extends APIService {
  //定义构造函数，调用父类的构造函数，传入NEXT_PUBLIC_API_BASE_URL或者"http://localhost:8000"
  constructor() {
    super(NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000");
  }

  //定义emailLogin方法，用于邮箱登录，调用父类的post方法，传入"/api/sign-in/"和data，
  async emailLogin(data: any) {
    return this.post("/api/sign-in/", data, { headers: {} })
      .then((response) => {
        this.setAccessToken(response?.data?.access_token);
        this.setRefreshToken(response?.data?.refresh_token);
        return response?.data;
      })
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  //定义socialAuth方法，用于社交登录，调用父类的post方法，传入"/api/social-auth/"和data，
  async socialAuth(data: any) {
    return this.post("/api/social-auth/", data, { headers: {} })
      .then((response) => {
        this.setAccessToken(response?.data?.access_token);
        this.setRefreshToken(response?.data?.refresh_token);
        return response?.data;
      })
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  //定义emailCode方法，用于邮箱验证码登录，调用父类的post方法，传入"/api/magic-generate/"和data，
  async emailCode(data: any) {
    return this.post("/api/magic-generate/", data, { headers: {} })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
  //定义magicSignIn方法，用于链接登录，调用父类的post方法，传入"/api/magic-sign-in/"和data，
  async magicSignIn(data: any) {
    const response = await this.post("/api/magic-sign-in/", data, { headers: {} });
    if (response?.status === 200) {
      this.setAccessToken(response?.data?.access_token);
      this.setRefreshToken(response?.data?.refresh_token);
      return response?.data;
    }
    throw response.response.data;
  }

  //定义refreshToken方法，用于刷新token，调用父类的post方法，传入"/api/refresh-token/"和data
  async signOut() {
    return this.post("/api/sign-out/", { refresh_token: this.getRefreshToken() })
      .then((response) => {
        this.purgeAccessToken();
        this.purgeRefreshToken();
        return response?.data;
      })
      .catch((error) => {
        this.purgeAccessToken();
        this.purgeRefreshToken();
        throw error?.response?.data;
      });
  }
}

export default new AuthService();
