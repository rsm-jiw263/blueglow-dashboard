# 🌟 Blue Tears Dashboard - 部署完整指南

## 📊 项目概述

La Jolla Blue Tears 商业可行性分析仪表板 - MGTA 452 期末项目

**特点**：
- ✅ 完全英文界面，专业商务风格
- ✅ 交互式数据可视化
- ✅ 实时策略模拟器
- ✅ 响应式设计，支持移动端

---

## 🎯 三种部署方式对比

| 方案 | 难度 | 费用 | 速度 | 适用场景 |
|------|------|------|------|----------|
| **Streamlit Cloud** | ⭐ 最简单 | 免费 | 5分钟 | ✅ **推荐** 公开分享 |
| **本地网络** | ⭐⭐ 简单 | 免费 | 1分钟 | 课堂演示/局域网 |
| **Heroku** | ⭐⭐⭐ 中等 | 免费/付费 | 10分钟 | 需要自定义域名 |

---

## 🚀 方案一：Streamlit Cloud（推荐）

### 为什么选择 Streamlit Cloud？
- ✅ **完全免费**（1GB 存储 + 1GB 内存）
- ✅ **零配置**，自动部署
- ✅ **https 加密**连接
- ✅ **全球 CDN**，访问速度快
- ✅ **自动更新**，push 代码即更新

### 详细步骤

#### Step 1: 准备 GitHub 仓库

**1.1 创建仓库**
```
访问：https://github.com/new

仓库名：blueglow-dashboard
描述：La Jolla Blue Tears Commercial Feasibility Dashboard
可见性：✅ Public（必须是公开仓库）
不要勾选：Initialize with README
```

**1.2 本地推送**

使用自动化脚本：
```bash
./deploy_auto.sh
```

或手动操作：
```bash
# 初始化
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 连接远程仓库（替换成你的地址）
git remote add origin https://github.com/YOUR_USERNAME/blueglow-dashboard.git

# 推送
git branch -M main
git push -u origin main
```

#### Step 2: 部署到 Streamlit Cloud

**2.1 登录 Streamlit Cloud**
```
访问：https://share.streamlit.io
点击：Sign in with GitHub
授权：Allow access
```

**2.2 创建新应用**
```
点击：New app
选择仓库：YOUR_USERNAME/blueglow-dashboard
Branch：main
Main file path：app_en.py
```

**2.3 高级设置（Advanced settings）**
```
Python version：3.9 或更高
Requirements file：requirements_streamlit.txt
（可选）Secrets：如需添加密码保护等
```

**2.4 部署**
```
点击：Deploy!
等待：3-5 分钟（首次部署）
```

#### Step 3: 完成！

应用地址：
```
https://YOUR_USERNAME-blueglow-dashboard.streamlit.app
```

### 🔄 如何更新？

非常简单！修改代码后：

```bash
git add .
git commit -m "Update dashboard"
git push
```

Streamlit Cloud 会**自动检测**并重新部署！

---

## 💻 方案二：本地网络共享

适合课堂演示或局域网内分享。

### 快速开始

**1. 查看本机 IP**
```bash
# Mac/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# 或 Mac 快捷方式
ipconfig getifaddr en0

# Windows
ipconfig
```

假设你的 IP 是：`192.168.1.100`

**2. 启动应用**
```bash
streamlit run app_en.py --server.address 0.0.0.0
```

**3. 分享链接**
```
http://192.168.1.100:8501
```

同一 WiFi 的人都可以访问！

### 适用场景
- ✅ 课堂演示
- ✅ 团队内部预览
- ✅ 无需互联网

---

## 🌍 方案三：Heroku（备选）

需要信用卡验证（不扣费），适合需要自定义域名的场景。

### 前置准备

**安装 Heroku CLI**
```bash
# Mac
brew install heroku/brew/heroku

# Windows/Linux
# 访问：https://devcenter.heroku.com/articles/heroku-cli
```

### 部署步骤

**1. 创建 Procfile**
```bash
cat > Procfile << EOF
web: sh setup.sh && streamlit run app_en.py
EOF
```

**2. 创建 setup.sh**
```bash
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
EOF
```

**3. 部署**
```bash
# 登录
heroku login

# 创建应用
heroku create blueglow-dashboard

# 推送
git push heroku main

# 打开
heroku open
```

应用地址：
```
https://blueglow-dashboard.herokuapp.com
```

---

## 📱 方案四：其他云平台

### Railway
```
1. 访问：https://railway.app
2. Connect GitHub repo
3. 自动部署
```

### Render
```
1. 访问：https://render.com
2. New Web Service
3. 连接 GitHub
```

### Vercel
```
1. 访问：https://vercel.com
2. Import Project
3. 自动部署
```

---

## 🔐 安全设置

### 添加密码保护

**1. 创建 secrets.toml**
```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
password = "blueglow2024"
EOF
```

**2. 在 app_en.py 添加认证**
```python
import streamlit as st

# 在文件开头添加
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()

# 你的应用代码...
```

**3. 在 Streamlit Cloud 添加 Secret**
```
App Settings → Secrets → 添加：
password = "blueglow2024"
```

---

## 🎨 自定义域名

### Streamlit Cloud（企业版）
需要升级到 Team/Enterprise 计划

### 使用 Cloudflare（免费）
```
1. 在 Cloudflare 添加 CNAME 记录
2. 指向你的 Streamlit 应用
3. 启用 SSL
```

### 使用 Vercel
```
1. 部署到 Vercel
2. Settings → Domains
3. 添加自定义域名
```

---

## 🐛 常见问题排查

### 问题 1：应用无法启动
```bash
# 检查依赖
python3 check_deployment.py

# 测试本地运行
streamlit run app_en.py
```

### 问题 2：数据文件找不到
```
确保 streamlit_data/ 文件夹在 Git 仓库中：
git add streamlit_data/*.csv -f
git commit -m "Add data files"
git push
```

### 问题 3：Git 推送失败
```bash
# 检查远程仓库
git remote -v

# 重新设置
git remote remove origin
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 问题 4：Streamlit Cloud 构建失败
```
检查：
1. requirements_streamlit.txt 是否正确
2. Python 版本是否兼容（建议 3.9+）
3. 查看 Build logs 错误信息
```

---

## 📊 性能优化

### 数据缓存
代码中已使用 `@st.cache_data` 装饰器

### 减小数据文件
```bash
# 如果 CSV 太大，可以压缩
gzip streamlit_data/*.csv

# 在代码中读取
import gzip
df = pd.read_csv(gzip.open('data.csv.gz'))
```

### 使用外部数据源
```python
# 从 Google Sheets 读取
import gspread
# 从 S3 读取
import boto3
```

---

## 📞 获取帮助

- **Streamlit 文档**: https://docs.streamlit.io
- **社区论坛**: https://discuss.streamlit.io
- **GitHub Issues**: https://github.com/streamlit/streamlit/issues

---

## ✅ 部署检查清单

在部署前，确保：

- [ ] 运行 `python3 check_deployment.py` 通过
- [ ] 本地测试 `streamlit run app_en.py` 正常
- [ ] 所有数据文件已添加到 Git
- [ ] requirements_streamlit.txt 包含所有依赖
- [ ] GitHub 仓库是 Public
- [ ] 已测试基本功能（加载数据、切换 Tab）

---

## 🎉 准备好了吗？

### 快速开始（推荐）

```bash
# 运行自动部署脚本
./deploy_auto.sh
```

### 或查看详细步骤

阅读 `DEPLOYMENT_GUIDE_CN.md` 完整教程

---

**祝部署顺利！🚀**

有问题随时查看文档或在课堂上提问。
