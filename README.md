# SEU·绩点计算器

@X_Y
<img width="1920" height="1319" alt="7e919bedecc2dc4acf4c3e88a0213e8c" src="https://github.com/user-attachments/assets/116aaac6-e812-476c-8944-ac5b036c5ccb" />


双击 `SEU·绩点计算器.bat` 打开，也可运行 `python "SEU·绩点计算器.py"`。
需要 Python 3.10+（含 Tkinter）。缺少联网依赖时运行：

```powershell
python -m pip install requests
```

- 支持教务登录获取、手动录入、课程编辑、搜索筛选和导入导出。
- 同时显示 4.0 / 4.8 制 GPA、加权均分和均分对应参考绩点，采用分段换算，不插值。
- 提供成绩分布、学期对照和目标均分预测。

点击“保存记录”或按 `Ctrl+S`，每次生成一份 `log/日期_时间.json`，不会自动保存或覆盖历史文件。重新打开时恢复最近一次保存。

`log` 文件夹可直接删除，历史记录随之清空，不影响软件运行；下次手动保存时会自动重建。

获取失败时，请检查 VPN / 代理设置是否影响教务访问。
