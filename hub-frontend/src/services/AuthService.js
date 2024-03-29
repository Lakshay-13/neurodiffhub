import React, { useState, useEffect, useContext, useReducer, createContext } from "react";
import { useHistory } from 'react-router-dom';

import { BASE_API_URL } from "./Common";

const axios = require('axios');

export const authHeader = () => {
    const auth = JSON.parse(localStorage.getItem('auth'));

    if (auth && auth.access_token) {
        return { Authorization: 'Bearer ' + auth.access_token };
    } else {
        return {};
    }
}

// Local Storage Hook
function useLocalStorage(key, initialValue) {
    // State to store our value
    // Pass initial state function to useState so logic is only executed once
    const [storedValue, setStoredValue] = useState(() => {
        try {
            // Get from local storage by key
            const item = window.localStorage.getItem(key);
            // Parse stored json or if none return initialValue
            return item ? JSON.parse(item) : initialValue;
        } catch (error) {
            // If error also return initialValue
            console.log(error);
            return initialValue;
        }
    });
    // Return a wrapped version of useState's setter function that ...
    // ... persists the new value to localStorage.
    const setValue = (value) => {
        try {
            // Allow value to be a function so we have same API as useState
            const valueToStore =
                value instanceof Function ? value(storedValue) : value;
            // Save state
            setStoredValue(valueToStore);
            // Save to local storage
            window.localStorage.setItem(key, JSON.stringify(valueToStore));
        } catch (error) {
            // A more advanced implementation would handle the error case
            console.log(error);
        }
    };
    return [storedValue, setValue];
}

// Create an Auth Context
const AuthContext = createContext();

// Hook for child components to get the auth object
// and re-render when it changes.
export const useAuthContext = () => {
    return useContext(AuthContext);
};

// Setup Auth Reducer
let initialState = {
    isAuthenticated: false,
    username: null,
    full_name: null,
    access_token: null,
    token_type: null,
    account_type: null
};
const reducer = (state, action) => {
    switch (action.type) {
        case "LOGIN":
            localStorage.setItem("auth", JSON.stringify(action.payload));
            return {
                ...state,
                isAuthenticated: true,
                username: action.payload.username,
                access_token: action.payload.access_token,
                full_name: action.payload.full_name,
                account_type: action.payload.account_type
            };
        case "LOGOUT":
            localStorage.clear();
            return {
                ...state,
                isAuthenticated: false,
                username: null,
                account_type: null
            };
        case "PROFILE":
            return {
                ...state,
                full_name: action.payload.full_name,
                account_type: action.payload.account_type
            };
        default:
            return state;
    }
};

// Auth Context Provider component that wraps your app and makes auth object
// available to any child component that calls useAuth().
export function AuthContextProvider({ children }) {
    console.log("================================== AuthContextProvider ======================================");

    // Check if user was already logged in in local storage
    const auth = JSON.parse(localStorage.getItem('auth') || null);
    if (auth) {
        initialState["isAuthenticated"] = true;
        initialState["username"] = auth.username;
        initialState["access_token"] = auth.access_token;
    }

    // Auth Reducer
    const [state, dispatch] = useReducer(reducer, initialState);

    // Setup Provider
    useEffect(() => {
        console.log(state);
        if (state.isAuthenticated) {
            // Validate Auth
            AuthService.Validate()
                .then(function (response) {
                    console.log(response.data);
                    dispatch({
                        type: "LOGIN",
                        payload: response.data
                    })

                    // Get User Profile
                    return AuthService.GetProfile()
                })
                .then(function (response) {
                    let profile = response.data;
                    dispatch({
                        type: "PROFILE",
                        payload: profile
                    })
                })
                .catch(function (error) {
                    console.log(error.response);
                    dispatch({
                        type: "LOGOUT"
                    })
                })
        }
    }, []);

    return <AuthContext.Provider value={{ state, dispatch }}>{children}</AuthContext.Provider>;
}

// Provider hook that creates auth object and handles state
export const useProvideAuth = () => {
    const [user, setUser] = useState(null);
    const [auth, setAuth] = useLocalStorage("auth", null);

    let history = useHistory();

    const login = (username, password) => {
        return {};
    };
    const signup = (username, password) => {
        return {};
    };
    const logout = () => {
        return {};
    };
    const verify = () => {
        if (!user) {
            history.push("/login");
        }
    }
    const valid = () => {
        if (!user) {
            return false;
        } else {
            return true;
        }
    }

    // Subscribe to user on mount
    // Because this sets state in the callback it will cause any ...
    // ... component that utilizes this hook to re-render with the ...
    // ... latest auth object.
    useEffect(() => {
        const auth = JSON.parse(localStorage.getItem('auth'));
        console.log(auth);
        if (auth) {
            setUser(auth.username);
        }
    }, []);

    // Return the user object and auth methods
    return {
        user,
        login,
        signup,
        logout,
        verify,
        valid,
    };
}

const AuthService = {
    Init: function () {
        // Any application initialization logic comes here
    },
    Signup: async function (username, email, password,) {
        
        if (username=='') {username=' ';}
        if (password=='') {password=' ';}
        if (email=='') {email=' ';}
        var formData = new FormData();
        formData.append("grant_type", "password");
        formData.append("username", username);
        formData.append("password", password);
        formData.append("email", email);

        return await axios.post(BASE_API_URL + "/auth/signup",
            formData,
            {
                headers: { "Content-Type": "application/x-www-form-urlencoded" }
            }
        );
    },
    Login: async function (username, password,) {

        var formData = new FormData();
        formData.append("grant_type", "password");
        formData.append("username", username);
        formData.append("password", password);

        return await axios.post(BASE_API_URL + "/auth/login",
            formData,
            {
                headers: { "Content-Type": "application/x-www-form-urlencoded" }
            }
        );
    },
    Validate: async function () {
        return await axios.post(BASE_API_URL + "/auth/validate", {}, { headers: authHeader() });
    },
    GetProfile: async function () {
        return await axios.get(BASE_API_URL + "/profile", { headers: authHeader() });
    },
    SaveProfile: async function (profile) {
        return await axios.put(BASE_API_URL + "/profile", profile, { headers: authHeader() });
    },
    GetAccount: async function () {
        return await axios.get(BASE_API_URL + "/account", { headers: authHeader() });
    },
    SaveAccount: async function (account) {
        return await axios.put(BASE_API_URL + "/account", account, { headers: authHeader() });
    },
    GetAPIKeys: async function () {
        return await axios.get(BASE_API_URL + "/api_keys", { headers: authHeader() });
    },
    CreateAPIKey: async function () {
        return await axios.post(BASE_API_URL + "/api_keys", {}, { headers: authHeader() });
    },
    DeleteAPIKey: async function (id) {
        return await axios.delete(BASE_API_URL + "/api_keys/" + id, { headers: authHeader() });
    },
    ResetPassword: async function (email) {
        return await axios.post(BASE_API_URL + "/auth/resetpassword", { "email": email }, { headers: authHeader() });
    },
}
export default AuthService;