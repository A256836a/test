部署说明（快速修复指南）

目标：解决 Streamlit Cloud 部署时常见的依赖与 API Key 问题，确保应用能上线并在缺少模型 Key 时降级运行。

必须步骤：
1. 在 Streamlit Cloud 的应用设置中，设置环境变量：
   - 名称：DASHSCOPE_API_KEY
   - 值：你的 dashscope API Key

2. 固定 Python 版本：仓库根目录已配置 `runtime.txt`（`python-3.12.8`）与 `.python-version`（`3.12`）。**若应用是在 Streamlit Cloud 上早期创建的，可能仍运行在 Python 3.14**——请在部署时于 Advanced 中选择 Python 3.12，或删除应用后重新部署以应用版本设置。

3. 确保 `requirements.txt` 使用较新的 Streamlit（`>=1.41.0`），**不要**再锁定 `streamlit==1.21.0` 或 `pillow==9.5.0`（会在新 Python 上触发源码编译失败）。

4. 如果你不想使用外部模型或不想处理 API Key，可选择删除 `dashscope` 行并保留仓库中已实现的降级/模拟逻辑，应用会以降级模式启动。

故障排查：
- 错误：Could not build wheels for pillow / zlib missing
  解决：使用 `python-3.10.12` 的 runtime 或让平台提供含二进制 wheel 的环境；也可在 requirements 中降级 streamlit 版本到 platform 提供 wheel 的版本。

- 错误：401 Invalid API-key provided
  解决：确认 Streamlit Cloud 环境变量 `DASHSCOPE_API_KEY` 填写正确，且无多余空格；重新部署。

- 错误：ModuleNotFoundError: No module named 'dashscope'
  解决：确保 `dashscope` 在 `requirements.txt` 中且 redeploy 时 pip 能成功安装（参照上方 runtime 固定以避免编译问题）。

部署顺序（建议）：
1. 在 Streamlit Cloud 设置 runtime（仓库已更新）。
2. 在 Settings -> Advanced -> Environment variables 添加 `DASHSCOPE_API_KEY`。
3. Redeploy。

如果需要，我可以：
- 在仓库根添加 `README_DEPLOY.md`（更详细部署脚本）。
- 移除或注释 `dashscope` 在 `requirements.txt`（如果你明确不使用外部模型）。
