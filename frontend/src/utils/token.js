import Cookies from "js-cookie";

const ACCESS_KEY = "chatsphere_access_token";
const REFRESH_KEY = "chatsphere_refresh_token";

export const getAccessToken = () => Cookies.get(ACCESS_KEY);
export const getRefreshToken = () => Cookies.get(REFRESH_KEY);

export const setTokens = (accessToken, refreshToken) => {
    Cookies.set(ACCESS_KEY, accessToken, { expires: 1, sameSite: "Lax" });
    Cookies.set(REFRESH_KEY, refreshToken, { expires: 7, sameSite: "Lax" });
};

export const removeTokens = () => {
    Cookies.remove(ACCESS_KEY);
    Cookies.remove(REFRESH_KEY);
};
