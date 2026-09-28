# NeuroTrace 原型

先运行流程，再接模型和真实论文。交接包样例始终标记为演示资料。

## 启动

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

本机已准备 `.venv` 时，可使用 `.venv/Scripts/python.exe`（Windows）。

打开 http://127.0.0.1:8501。默认演示模式不需要模型。切换到 Ollama 后填写实际服务地址和已安装模型名；失败会明确报告，不会替换成演示结果。

PDF 模式：在侧栏选择“我上传的 PDF”，上传并解析后调查。PDF 保存到 `data/pdfs`，索引和案件保存在当前浏览器会话；重要结果请导出。当前不支持 OCR、跨会话历史及内嵌 PDF 高亮。

## Spark

建议开发阶段保持本机监听，通过 SSH 隧道访问。公网演示前设置 `NEUROTRACE_PASSWORD`，并按实际节点映射选择端口和 `0.0.0.0` 监听地址。不要复制旧手册中的示例账号或端口。模型接口无需公开。

可选环境变量：`OLLAMA_BASE_URL`、`OLLAMA_MODEL`、`NEUROTRACE_PASSWORD`。

## 验证

```sh
python -m unittest discover -s tests -v
```

当前算法是原型：关键词检索、逐卡模型关系、保守规则聚合。样例标签不会因人工点击变成正式证据；真实 PDF 的页码、原文与哈希在导出前重新核验。尚未完成领域准确率评测。
