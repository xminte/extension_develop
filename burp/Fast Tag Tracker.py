# -*- coding: utf-8 -*-

from burp import IBurpExtender, ITab, IHttpListener
from javax.swing import JPanel, JTable, JScrollPane, JButton, BoxLayout, JOptionPane, JTextField
from javax.swing.table import DefaultTableModel
from java.awt.event import ActionListener
import os

class BurpExtender(IBurpExtender, ITab, IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        """
        初始化扩展回调
        """
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("Fast Tag Tracker")
        
        print("欢迎使用关键词计数器！")  # 初次安装启动时打印消息
        
        # 初始化主面板
        self._panel = JPanel()
        self._panel.setLayout(BoxLayout(self._panel, BoxLayout.Y_AXIS))
        
        # 初始化默认标签关键词
        self._tag_keywords = ["input", "form"]  # 默认标签关键词
        self.update_table_model()  # 更新表格模型
        
        # 创建并添加表格
        self._table = JTable(self._table_model)
        self._table.setAutoCreateRowSorter(True)
        scroll_pane = JScrollPane(self._table)
        self._panel.add(scroll_pane)
        
        # 创建并添加设置按钮
        settings_button = JButton('Settings')
        settings_button.addActionListener(self.show_settings_dialog)
        self._panel.add(settings_button)
        
        # 自定义UI组件并添加到Burp Suite
        self._callbacks.customizeUiComponent(self._panel)
        self._callbacks.addSuiteTab(self)
        self._callbacks.registerHttpListener(self)

    def getTabCaption(self):
        """
        获取标签标题
        """
        return "Fast Tag Tracker"
    
    def getUiComponent(self):
        """
        获取UI组件
        """
        return self._panel
    
    def update_table_model(self):
        """
        更新表格模型，根据标签关键词动态生成列
        """
        column_names = ["URL"] + ["{} Tag Count".format(tag.capitalize()) for tag in self._tag_keywords]
        self._table_model = DefaultTableModel(column_names, 0)

    def show_settings_dialog(self, event):
        """
        显示设置对话框，让用户输入标签关键词
        """
        tag_input = JTextField(",".join(self._tag_keywords), 20)
        panel = JPanel()
        panel.add(tag_input)
        result = JOptionPane.showConfirmDialog(self._panel, panel, "Enter tags to count (comma separated)", JOptionPane.OK_CANCEL_OPTION)
        if result == JOptionPane.OK_OPTION:
            self._tag_keywords = [tag.strip() for tag in tag_input.getText().split(",")]
            self.update_table_model()
            self._table.setModel(self._table_model)
            self._table.repaint()

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        """
        处理HTTP消息，统计指定标签的数量
        """
        if not messageIsRequest:
            response = messageInfo.getResponse()
            if response:
                response_info = self._helpers.analyzeResponse(response)
                mime_type = response_info.getStatedMimeType()
                
                if mime_type and mime_type.lower() in ['html', '']:
                    response_body = messageInfo.getResponse()[response_info.getBodyOffset():]
                    response_str = self._helpers.bytesToString(response_body)
                    
                    if any("<{} ".format(tag) in response_str for tag in self._tag_keywords):
                        url = messageInfo.getUrl().toString()
                        counts = [self.count_tags(response_str, tag) for tag in self._tag_keywords]
                        self.add_row_to_table(url, counts)

    def count_tags(self, html, tag):
        """
        统计指定标签在HTML中的数量
        """
        import re
        pattern = "<{0}[^>]*>".format(tag)
        return len(re.findall(pattern, html))
    
    def add_row_to_table(self, url, counts):
        """
        添加新行到表格模型
        """
        try:
            row_data = [url] + counts
            self._table_model.addRow(row_data)
        except Exception as e:
            print("Error adding row to table: {}".format(e))
