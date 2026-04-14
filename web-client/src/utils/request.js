import axios from 'axios'

const request = axios.create({
    baseURL: 'http://localhost:8080', // 你的 Spring Boot 端口
    timeout: 5000
})

// 响应拦截器：自动剥离后端的 Result 外壳
request.interceptors.response.use(
    response => {
        const res = response.data
        if (res.code === 200) {
            return res.data
        } else {
            alert(res.msg || '操作失败')
            return Promise.reject(new Error(res.msg))
        }
    },
    error => {
        alert('网络连接失败，请检查后端是否启动')
        return Promise.reject(error)
    }
)

export default request