# label_img_xml_modify_script

---

(完成) 存取手機內的檔案
(未完成) iOS->非同步呼叫camera和auto_predictor
(完成) Android crash
參考: 
- [codemy-kivy GUI tutorial](https://www.youtube.com/playlist?list=PLCC34OHNcOtpz7PJQ7Tv7hqFBP_xDDjqg)參考第#14部 update kivy .kv 檔的方法
- [kivy 資源](:/af0765d50f0e48859d9d6877f6333358)

## 頁首
kivy
- [kivy主程式 :Camera + autopredictor 拍照後傳回辨識檔案,使用 python kivy套件寫 iOS 和 Android APP](#kivy主程式)
<details>

	- 拍照
	- 切換螢幕頁面,使用 ScreenManager
	- 存取相簿
	- 非同步處理
	- filechooser 檔案總管
</details>

- [kivy for iOS](#iOS)
<details>

	- 安裝xcode
	- 申請 Apple developer ID
	- Build iOS App
	
		- (沒再發生可忽略)地雷1-1.使用 toolchain build kivy error
		- 重要! 地雷1-2.build `toolchain build python3 kivy` 仍然出現錯誤
	- Xcode Build 設定
		- 使用 script 協助找出之前可重複使用的bundle id
		- xcode 編譯出錯:　Command 		PhaseScriptExecution failed with a nonzero exit code
		- 地雷2. xcode Build 時發生 Command 		- 		- PhaseScriptExecution failed with a nonzero exit code
		- xcode Build 地雷3. unable to install app,could not write to the device
		- 重要! xcode Build 地雷4. ModuleNotFoundError==>toolchain pip install module名稱
		- xcode build 地雷 '.../dist/include/common/sdl2/SDL_main.h' file not found
		- xcode build 地雷 Running main.py:(null)
		- iOS 的背景執行(multiprocess)問題 AttributeError: module 'subprocess' has no attribute 'Popen'
</details>

- [kivy for android](#Android)
	- [安裝p4a](https://hackmd.io/@cssmiley/HkG29iGc3)
<details>

- kivy 在不同的頁面資料溝通
- 地雷: ModuleNotFoundError: No module named 'android'
- 地雷：存取檔案時出現錯誤exposed beyond app through ClipData.Item.getUri
- 地雷: 執行apk閃退出現錯誤
- (Android推薦使用)  [python for android](#p4a)
- kivy 移除開頭黑畫面,減少讀取時間
</details>


---
[回頁首](#頁首)
<h2 id="kivy主程式">kivy主程式 :Camera + autopredictor 拍照後傳回辨識檔案,使用 python kivy套件寫 iOS 和 Android APP</h2>

流程:
拍照 -> 切換螢幕頁面 -> 開啟 filechooser -> 存取相簿 -> 背景執行 -> 使用 autopredictor處理上傳辨識 -> 回存到相簿

<details> <summary>拍照</summary>

[Gallery of Examples » Camera Example¶](https://kivy.org/doc/stable/examples/gen__camera__main__py.html)
可參考官方的呼叫 Camera 範例:
```
File camera/main.py¶

'''
Camera Example
==============

This example demonstrates a simple use of the camera. It shows a window with
a buttoned labelled 'play' to turn the camera on and off. Note that
not finding a camera, perhaps because gstreamer is not installed, will
throw an exception during the kv language processing.

'''

# Uncomment these lines to see all the messages
# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')


class CameraClick(BoxLayout):
    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        print("Captured")


class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()
```

其中儲存影像的code => camera.export_to_png( )需要修改成 camera.texture.save( )
[Modify way of saving images in the example with camera](https://github.com/kivy/kivy/issues/7872)
```
因為 camera.export_to_png( ) 會造成 camera 捕捉的 image 被縮放到跟 widget 一樣的 size, 改成 camera.texture.save( ) 則會直接儲存從 camera捕捉到的版本
```
---

</details>


<details> <summary>切換螢幕頁面,使用 ScreenManager</summary>

[Kivy Tutorial #9 - Navigation Between Multiple Screens](https://www.youtube.com/watch?v=xaYn4XdieCs&list=PLzMcBGfZo4-kSJVMyYeOQ8CXJ3z1k7gHn&index=9)

基本例子:
- main.py
```
from kivy.uix.screenmanager import ScreenManager, Screen

kv = Builder.load_file("main.kv")

class MainWindow(Screen):
	pass

class SecondWindow(Screen):
	pass

class WindowManager(ScreenManager):
	pass
```
- main.kv
```
WindowManager:
	MainWindow:
	SecondWindow:
<MainWindow>
	name: "main"
	
	Button:
		text: "submit"
		on_release: 
			app.root.current ="second"
			root.manager.transition.direction ="left"
<SecondWindow>
	name: "second"
	Button:
		text: "Go Back"
		on_release: 
			app.root.current ="main"
			root.manager.transition.direction ="right"
```

存取不同螢幕頁面class的元件
[Kivy: How To Access Widgets From Another Class or Another Screen](https://www.youtube.com/watch?v=DSMzCsnocn0)

基本例子:
- main.py
```
from kivy.uix.screenmanager import ScreenManager, Screen
self.manager.get_screen("second").ids.filechooser.rootpath
```
-main.kv
```
<SecondWindow>:
    name: "second"

    FileChooserIconView
        id: filechooser
        rootpath:""
```
---

</details>

<details> <summary>存取相簿 </summary>

參考網址:
[Image Viewer With FileChooserIconView and FileChooserListView - Python Kivy GUI Tutorial #23](https://www.youtube.com/watch?v=YlRd4rw_vBw&list=PLCC34OHNcOtpz7PJQ7Tv7hqFBP_xDDjqg&index=23)

[Android Storage Access Framework in Python kivy](https://stackoverflow.com/questions/67129296/storage-access-framework-in-python)

---推薦使用---
 [Access android storage path, Request Storage Permission, and compile APK using Pyjnius and Buildozer](https://www.youtube.com/watch?v=bYaIFQdpEsI)
基本例子.
- p4a (python for android) 下參數
```
--permission android.permission.WRITE_EXTERNAL_STORAGE \
--permission android.permission.READ_EXTERNAL_STORAGE \
--permission android.permission.CAMERA \
```
- main.py
```
from jnius import autoclass
Environment = autoclass("android.os.Environment")
path = Environment.getExternalStorageDirectory().getAbsolutePath()
```

(?) 測試不需要這一段要求permission(在p4a要求即可) 
- main.py
```
from android.permission import requesr_permission,Permission
class Main(MDApp):
	def on_start(self):
		request_permission([Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE])
```

用 Environment.getExternalStorageDirectory( ) 取代 Environment.getExternalStorageDirectory( )
[Environment.getExternalStorageDirectory() is deprecated过时的替代方案](https://blog.csdn.net/shving/article/details/101057082)
```
getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES)
```

[（一看就懂）Environment.getExternalStorageDirectory() is deprecated](https://blog.51cto.com/u_15657752/5335022)
```
Environment.getExternalStorageDirectory()获取根路径的方式不友好，比如app删除，app对应的图片不删除，保存路径是sd卡根路径

 替代方案

getExternalFilesDir(Environment.DIRECTORY_PICTURES) 注意：前面没有Environment，app删除对应的图片相应删除，保护隐私，保存路径是
/storage/emulated/0/Android/data/com.wintec.huashang/files/Pictures

etExternalFilesDir(null)则为：/storage/emulated/0/Android/data/com.wintec.huashang/files
 实测在android7.1.2的系统上String sdPath = Environment.getExternalStorageDirectory().getAbsolutePath()+"/a/" ;这种方法已经无法创建文件路径

```

---

</details>

<details> <summary> Android 非同步處理 </summary>

[Android限定]
非同步處理:
(暫時用連結,確定解決非同步之後整個搬過來)
[python 非同步處理](:/d9132338c6f84e719b3f42caf4626ea4)
參考網址: [Creating an Android Background Service in Kivy Application](https://www.youtube.com/watch?v=f57ItZCtliM&t=329s)
 [python for android 的 背景運行service](https://python-for-android.readthedocs.io/en/latest/services/)
重要,main application 和 background service溝通:
- [Building a background application on android with Kivy.](https://blog.kivy.org/2014/01/building-a-background-application-on-android-with-kivy/)
- [Android for Python Users-Android service](https://github.com/Android-for-Python/Android-for-Python-Users#android-service)

基本例子.
- p4a 下參數
```
--service=Camerapredictor:myservice.py 
```
- main.py
```
@staticmethod
	def start_service():
		service = autoclass("org.test.myapp.ServiceMyapp")
		mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
		service.start(mActivity, "")
		return service

# 必須要在 on_start() 啟動service才能有效運行(相當於android java code 的 on_create)
def on_start(self):
	from kivy import platform
	if platform == "android":
		self.start_service()
```
- myservice.py
```
from jnius import autoclass

PythonService = autoclass("org.kivy.android.PythonService")
PythonService.mService.setAutoRestartService(True)

while True:
print("service running...")
#do spmething
```
---
非同步溝通

- 非同步在activity 和 service 傳送訊息:
(版本過舊已淘汰,但可參考方法)[Building a background application on android with Kivy](https://blog.kivy.org/2014/01/building-a-background-application-on-android-with-kivy/)

```
kivy android背景執行時可以用service執行,但是啟動以後要讓androdi Activity 和 service 溝通
,在 android 會使用 Broadcast 來做到,但是要用kivy pyjunius 做到不容易.
另一個方法是用 network 來做,在 Service 假server,在Activity 當 client 端,利用 twisted 溝通,但這麼做殺雞用牛刀,而且把 Twisted 包進來太肥大

比較好的方法是用osc
OSC is a simple connectionless network protocol, that allow you to pack messages, and send them to an ip/port/api URI, turns out we don’t need anything more, and a connectionless protocol avoid us dealing with disconnections (like the UI being closed, or the service not being started yet) that could give us some headaches

(目前可以使用)[oscpy](https://github.com/kivy/oscpy)
A modern implementation of OSC for python2/3.
過程須把 str 轉換成 binary 做傳送[How to convert 'binary string' to normal string in Python3](https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3)
What is OSC.

OpenSoundControl is an UDP based network protocol, that is designed for fast dispatching of time-sensitive messages, as the name suggests, it was designed as a replacement for MIDI, but applies well to other situations. The protocol is simple to use, OSC addresses look like http URLs, and accept various basic types, such as string, float, int, etc. You can think of it basically as an http POST, with less overhead.

You can learn more about OSC on OpenSoundControl.org
```

基本例子.
- Server 端
```
from oscpy.server import OSCThreadServer
from time import sleep

osc = OSCThreadServer()
sock = osc.listen(address='0.0.0.0', port=8000, default=True)

@osc.address(b'/address')
def callback(*values):
    print("got values: {}".format(values))

sleep(1000)
osc.stop()
```
- Client 端
```
from oscpy.client import OSCClient

address = "127.0.0.1"
port = 8000

osc = OSCClient(address, port)
# send_message 傳binary, str 需轉成 binary 傳送
_str = "Hello World!"
binary = _str.encode('utf-8')
for i in range(10):
    osc.send_message(b'/address', binary)
```
---

</details>

<details> <summary>( 未完成) ios非同步處理 </summary>

[iOS限定]

---

非同步在activity 和 service 傳送訊息

</details>

<details> <summary>filechooser 檔案總管 </summary>

FileChooser
[Image Viewer With FileChooserIconView and FileChooserListView - Python Kivy GUI Tutorial #23](https://www.youtube.com/watch?v=YlRd4rw_vBw)
基本例子.
- main.py
```
Builder.load_file("main.kv")
class MyLayout(Widget):
	def selected(self, filename):
		try:
			self.ids.my_image.source = filename[0]
			print(filename[0])
		except:
			pass
```
- main.kv
```
<MyLayout>
	id: my_widget
	BoxLayout:
		orientation: "vertical"
		size: root.width, root.height
		Image:
			id: my_image
			source: ""

		FileChooserIconView:
			id: filechooser
			on_selection: my_widget.selected(filechooser.selection)
```
---

</details>

---
[回頁首](#頁首)
<h2 id="iOS">kivy for iOS</h2>

- 安裝xcode
- 申請 Apple developer ID 
- Build iOS App
- Xcode Build 設定

### 安裝xcode
[Xcode 管理學——下載 Xcode-13,波肥](https://weakself.dev/episodes/85)
[如何管理 Xcode 版本才不會害到自己跟團隊](https://13h.tw/2019/11/01/manage-xcode-versions.html)
延伸學習: [How to Write iOS Apps Without Xcode
Did you know you have iOS IDE options?](https://betterprogramming.pub/writing-ios-apps-without-xcode-89450d0de21a)
### 申請 Apple Developer ID
[申請 Apple Developer ID](https://www.actualidadiphone.com/zh-TW/como-crear-una-cuenta-de-desarrollador-de-apple-para-usarla-en-xcode/)

### Build iOS App
[Programming Guide » Create a package for iOS¶](https://kivy.org/doc/stable/guide/packaging-ios.html)

#### Prerequisites
```
$ brew install autoconf automake libtool pkg-config
$ brew link libtool
$ pip install Cython==0.29.28
```
#### Compile the distribution
```
$ pip install kivy-ios
$ toolchain build kivy
```

<details> <summary>(沒再發生可忽略)地雷1-1.使用 toolchain build kivy error</summary>

### 地雷1-1.使用 toolchain build kivy error

```
[DEBUG   ] New State: hostopenssl.build.x86_64 at 2023-01-15 14:02:27.948985
[INFO    ] Install include files for hostopenssl
[INFO    ] Install_include hostopenssl
[DEBUG   ] New State: hostopenssl.install_include at 2023-01-15 14:02:27.951146
[INFO    ] Install frameworks for hostopenssl
[INFO    ] Install_frameworks hostopenssl
[DEBUG   ] New State: hostopenssl.install_frameworks at 2023-01-15 14:02:27.954295
[INFO    ] Install sources for hostopenssl
[INFO    ] Install_sources hostopenssl
[DEBUG   ] New State: hostopenssl.install_sources at 2023-01-15 14:02:27.956386
[INFO    ] Install python deps for hostopenssl
[INFO    ] Install_python_deps hostopenssl
[DEBUG   ] New State: hostopenssl.install_python_deps at 2023-01-15 14:02:27.958271
[INFO    ] Install hostopenssl
[DEBUG   ] New State: hostopenssl.build_all at 2023-01-15 14:02:28.211970
[INFO    ] Download libffi
[INFO    ] Downloading https://github.com/libffi/libffi/releases/download/v3.4.2/libffi-3.4.2.tar.gz
Traceback (most recent call last):
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/bin/toolchain", line 8, in <module>
    sys.exit(main())
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 1555, in main
    ToolchainCL()
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 1299, in __init__
    getattr(self, args.command)()
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 1368, in build
    build_recipes(args.recipe, ctx)
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 1142, in build_recipes
    recipe.execute()
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 701, in execute
    self.download()
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 74, in _cache_execution
    f(self, *args, **kwargs)
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 737, in download
    self.download_file(self.url.format(version=self.version), fn)
  File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py", line 477, in download_file
    urlretrieve(url, filename, report_hook)
  File "/Users/2020mac01/.pyenv/versions/3.9.5/lib/python3.9/urllib/request.py", line 1847, in retrieve
    block = fp.read(bs)
  File "/Users/2020mac01/.pyenv/versions/3.9.5/lib/python3.9/tempfile.py", line 474, in func_wrapper
    return func(*args, **kwargs)
ValueError: read of closed file
```

### 解決:
[error when I run toolchain build kiva python3 #629](https://github.com/kivy/kivy-ios/issues/629)
```
> toolchain distclean

> pip install https://github.com/kivy/kivy-ios/archive/refs/heads/master.zip
```

---

</details>

<details> <summary>重要! 地雷1-2.build `toolchain build python3 kivy`
仍然出現錯誤</summary>

### 地雷1-2.使用上面的 `pip install https://github.com/kivy/kivy-ios/archive/refs/heads/master.zip` 重新build `toolchain build python3 kivy"

使用上面的 `pip install https://github.com/kivy/kivy-ios/archive/refs/heads/master.zip` 重新build `toolchain build python3 kivy"
仍然出現錯誤
```
 File "/.../kivy-ios/toolchain.py", line 58, in shprint
    line_str = "\n".join(line.encode("ascii", "replace").decode().splitlines())
AttributeError: 'bytes' object has no attribute 'encode'
```
### 解決1-2

[AttributeError:'bytes' object has no attribute 'encode'](https://stackoverflow.com/questions/60368956/attributeerrorbytes-object-has-no-attribute-encode)
問題是原本的 toolcahin.py 是在 python2 執行,python2 中的 string 是隱式的 bytes 物件,但現在是在python3, python3 中的string 是unicode,所以toolchain.py第58行的`line_str = "\n".join(line.encode("ascii", "replace").decode().splitlines())` 原本預計是string物件的地方變成 bytes, 造成 encode 時出錯
修正: 在路徑 .../kivy-ios/toolchain.py (目前安裝在 /Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/kivy_ios/toolchain.py  
),把地58行的 `line_str = "\n".join(line.encode("ascii", "replace").decode().splitlines())`修改成
```
 if type(line) is bytes:
            line_str = "\n".join(line.decode("utf-8","replace").splitlines())
        elif type(line) is str or (sys.version_info[0] <3 and type(line) is unicode):
            line_str = "\n".join(line.encode("ascii", "replace").decode().splitlines())
        else:
            raise TypeError("Expected bytes or string, but got %s." % type(line))
```
就可以正常build

---

</details>


#### Create an Xcode project
在建立 Xcode 專案之前,先確認我們的主程式進入點檔案名稱必須是main.py

建立 xcode project, 把下面命令的 title 換成想要的專案名稱,不能使用空白或是禁止的特殊符號, 把 app_directory 置換成放主程式的 app 專案資料夾路徑

```
$ toolchain create <title> <app_directory>
```
例如.
```
$ toolchain create Touchtracer ~/code/kivy/examples/demo/touchtracer
```

名稱為`<title>-ios` 的資料夾會被建立,裡面包含 Xcode 專案,可以雙點裡面的 .xcodeproj 檔,或是使用指令如下開啟 Xcode專案:
```
$ open touchtracer-ios/touchtracer.xcodeproj
```
點 play 執行程式

#### Update the Xcode project (我們不需要用到可以略過這步)

如果想要新增第三方模組 (例如. numpy) 到自己的project, 但是並沒有在建立 Xcode project 之前就先 compile,那麼第一步要先 build:
```
$ toolchain build numpy
```
然後更新 Xcode project
```
$ toolchain update touchtracer-ios
```
所有必須用來執行所有被編譯的 recipes 的 libraries/frameworks 就會被加到 Xcode project 裡 

### Xcode Build 設定

#### 把 developer team 加入 xcode project
[把 developer team 加入 xcode project](https://developer.apple.com/forums/thread/64973)

1 - 到 Xcode Preferences 把 Apple ID account 加到 Xcode

![af7a4bd7-3d11-48fc-b8f6-63cbd5092094.png](https://i.imgur.com/uWNarAX.png)

2 - 點 Manage Certificates 後, 點左下方的 + 並點擊 Apple Development  

![be687877-a6e8-4f46-9bf2-17e27bf79a77.png](https://i.imgur.com/TLfVxAn.png)

3- 在 Project Navigator 點選我們的 Apps project , 然後點擊 "Signing & Capibilities" 
![eb0c5c67-6107-459c-babb-4884b2bb31fe.png](https://i.imgur.com/lqeaeoW.png)

4 - 最後點擊 Team 選擇自己的 developer team, 一般是自己的 (Personal Team) 

#### Xcode project Build settings

![スクリーンショット 2023-02-04 午後3.47.24.png](https://i.imgur.com/KfZcuLe.png)

這邊有幾個要注意的設定,沒有做到會導致 build failed

選擇project > Signing & Capibilies > Bundle Identifier

- (測試無效)添加後綴當作 child project ,例如. org.team.kive_camera 改成 org.team.kivy_camera.camera_child ([Failed to register bundle identifier
](https://developer.apple.com/forums/thread/130493))
- 如果 7 天內已經建立了 10 個 App ID 額度已滿,就要重複使用該developer team Build 過的 Bundle ID ([iOS真机运行错误“Your maximum App ID limit has been reached. You may create up to 10 App IDs every 7 days.”](https://www.jianshu.com/p/db1afeeb776d)),使用 script 協助找出之前可重複使用的bundle id 

<details> <summary>使用 script 協助找出之前可重複使用的bundle id </summary>
	## 使用bash 直接撈出 build 過的 bundle id

	[Parsing mobileprovision files in bash?](https://stackoverflow.com/questions/6398364/parsing-mobileprovision-files-in-bash/47763510#47763510)
	
	If your running this on a machine with mac os x, you can use the following:
	```
	/usr/libexec/PlistBuddy -c 'Print :Entitlements:application-identifier' /dev/stdin <<< $(security cms -D -i path_to_mobileprovision) 
	```
	
	I created a bash function based on jlawrie's answer to list all .mobileprovision's bundle IDs from the ~/Library/MobileDevice/Provisioning Profiles folder.
	
	Save this into your .bash_profile (For those who don't know how to insert that on .bash_profile, touch ~/.bash_profile; open ~/.bash_profile, copy and paste the source provided, save it, restart the terminal window )
	and just call it with `list_xcode_provisioning_profiles` from a terminal.
	```
	list_xcode_provisioning_profiles() {
		while IFS= read -rd '' f; do
			2> /dev/null /usr/libexec/PlistBuddy -c 'Print :Entitlements:application-identifier' /dev/stdin \
				<<< $(security cms -D -i "$f")
	
		done < <(find "$HOME/Library/MobileDevice/Provisioning Profiles" -name '*.mobileprovision' -print0)
	}
	```

---

</details>

- 如果手機安裝了多個自己帳號 build 的多個App,會超出額度無法安裝,需刪除手機內安裝的多個相同developer team 的 App([The maximum number of apps for free development profiles has been reached. Xcode 11.5](https://stackoverflow.com/questions/61953293/the-maximum-number-of-apps-for-free-development-profiles-has-been-reached-xcode))

<details> <summary> xcode 編譯出錯:　Command PhaseScriptExecution failed with a nonzero exit code</summary>

---
1. 本機空間不足
2. 主要是工作區已滿,導致編譯出錯參考下面說明:
[关于Xcode Command PhaseScriptExecution failed with a nonzero exit code 解决方案](安裝xcode地雷:appstore下載安裝xcode卡在更新中)

一、问题描述

使用 Xcode 进行代码编写，在进行项目开发拉下来新项目代码的时候编译的过程中一直在报下面这个错误。
```
Command PhaseScriptExecution failed with a nonzero exit code
```

通过在网上进行查找后，网上给出的大多数解决方法都是下面这样，但是我进行尝试后，问题不但没有得到解决，反而报了更多的错误，因此我又询问了导师，最终得到解决的方法。

运行一个项目时遇到了这个bug提示，一直编译不过去，这其实是一个Xcode10引起的bug。 解决方案： 在Xcode菜单栏选择File -> Workspace Setting -> Build System 选择Legacy Build System 重新运行即可。
**出现这个问题的主要原因是工作区已满，导致代码编译出现错误**，解决这个问题的方法大致有两种。

（1）进入到 Xcode 的代码工作缓存区文件夹中手动进行清理（容易出错，不建议）

（2）直接只用 Xcode 提供的清理方法，Xcode 清理完工作区后会自动将工作文件链接（不会出错，建议）

因为第二种方法比较容易操作，而且不大可能会出错，所以解决方法中我们直接使用这个方法来解决。


二、解决方案

1. 首先在 Product -> Scheme 中选择当前项目的主代码模块

2. 选择 Product -> Clean Build Folder 清理工作区

3. 之后再重新编译项目代码就可以了

</details>


<details> <summary>地雷2. xcode Build 時發生
Command PhaseScriptExecution failed with a nonzero exit code</summary>

### 解決2
[Command PhaseScriptExecution failed with a nonzero exit code](https://su3895623.medium.com/xcode-12-解決-command-phasescriptexecution-failed-with-a-nonzero-exit-code-3da22872627e)

到 Project setting targets > Build Phases > Run Script>
勾選 ☑For install builds only

![1*soYRMezHfxS00mZQzC6Rfw.webp](:/58cdf3a10b4747b3ba9d464267c26a2c)

如果是Xcode 12以下，勾選 Run script only when installing

![1*hLq4dZTxC4mI8mc3fwPIZw.webp](:/d0c4dc003c6743a68eaa9a26e330d5cc)

---

</details>

<details> <summary> xcode Build 地雷3. unable to install app,could not write to the device </summary>

[App installation failed: Could not write to the device](https://stackoverflow.com/questions/31002642/app-installation-failed-could-not-write-to-the-device)
- 刪除手機已安裝的相同 app
- 在 xcode 中 clean Build folder
```
Product -> Clean (Shift-Cmd-K)
```
- iphone 重開機
- 上面 toolchain create 時命名不要有 "-"
- toolchain create 的時候不要再專案資料夾內執行[Running main.py: (null), Unable to open main.py, abort](https://stackoverflow.com/questions/55902169/running-main-py-null-unable-to-open-main-py-abort)

---

</details>



<details> <summary>## 重要! xcode Build 地雷4. ModuleNotFoundError==>toolchain pip install module名稱 </summary>

[kivy 產生 app 後執行發生 ModuleNotFoundError 的處理方式](https://qiita.com/rorosawa255/items/ec77368839ef6f581c74)

ModuleNotFoundErrorについて

kivy-iosによって作成したプログラムをXcodeからエミュレーターや実機に転送し，アプリを起動しようとすると
```
ModuleNotFoundError: No module named '{モジュール名}'
```
というエラーが発生し，アプリが起動しないということがあります．
```
ex:ModuleNotFoundError: No module named 'requests'
```
解決方法

toolchain createを行ったディレクトリで，
bash
```
$ toolchain pip install <モジュール名>
```
を行う．
例えば，
bash
```
$ toolchain pip install requests
```

</details>

<details> <summary>xcode build 地雷 '.../dist/include/common/sdl2/SDL_main.h' file not found </summary> 

['SDL.h' file not found ](https://github.com/kivy/kivy-ios/issues/140)
```
toochain build sdl2
```
---

</details>

<details> <summary>xcode build 地雷 Running main.py:(null) </summary> 

檢查專案主程式檔案名稱是否main.py
---

</details>

<details> <summary>iOS 的背景執行(multiprocess)問題 AttributeError: module 'subprocess' has no attribute 'Popen' </summary>

原因：[Unable to use imported subprocess module #372](https://github.com/kivy/kivy-ios/issues/372)
```
I'm pretty sure the multi-processing is not supported on iOS. I remember reading a more detailed article, but this link serves to confirm...
https://forum.omz-software.com/topic/4638/permission-error-with-multiprocessing-process

Multi-processing is something Apple deliberately tries to prevent. From the article below: "Despite iOS being a multitasking OS, it does not support multiple processes for one app."

https://medium.com/flawless-app-stories/basics-of-parallel-programming-with-swift-93fee8425287
[Updated] Gave wrong link above
```
[Why does the python multiprocess/subprocess module not work?

](https://github.com/kivy/kivy-ios/blob/master/README.md#why-does-the-python-multiprocesssubprocess-module-not-work)
```
Why does the python multiprocess/subprocess module not work?

The iOS application model does not currently support multi-processing in a cross-platform compatible way. The application design focuses on minimizing processor usage (to minimize power consumption) and promotes an alternative concurrency model.

If you need to make use of multiple processes, you should consider using PyObjus to leverage native iOS functionals for this.
```
(測試結果失敗,造成閃退 Unable to open main.py, abort.)解法work around:(https://stackoverflow.com/questions/69252024/use-boto3-with-kivy-ios)
```
I have a workaround for this:

# monkeypatching the things that asyncio needs
import subprocess
subprocess.PIPE = -1  # noqa
subprocess.STDOUT = -2  # noqa
subprocess.DEVNULL = -3  # noqa
I have this set right after my kivy.require statement at the top of my main.py file and things work fine for me. I'm using kivy v1.11.0.dev0, git-Unknown, 20190421 though, so not latest master.
```

---

</details>

---
[回頁首](#頁首)
<h2 id="Android">kivy for Android</h2>

使用Android模擬器 [夜神模擬器](https://tw.bignox.com)
adb路徑:  /Applications/NoxAppPlayer.app/Contents/MacOS/adb


[Programming Guide » Create a package for Android¶](https://kivy.org/doc/stable/guide/packaging-android.html)

完整的Buildozer Documentation 參考 [Buildozer README]((https://github.com/kivy/buildozer)


### Buildozer (build android apk 工具)

下載並安裝 Buildozer
```
git clone https://github.com/kivy/buildozer.git
cd buildozer
sudo python setup.py install
```
在要 build 成 App 的 project 資料夾內執行
```
buildozer init
```
這會產生 buildozer.spec 檔,可以在裡面設定build configuration 設定傳到 python-for-android 的參數

<details> <summary>注意 buildozer.spec 項目重點</summary>
- requirements 須包含所有第三方套件,通常沒包含到會是crash主因, 例如:

```
requirements = python3,kivy,requests,bs4,tqdm,urllib3,charset_normalizer,certifi,docutils,idna,Kivy-Garden,Pygments,setuptools,soupsieve
```

- android.permissions 須包含會使用到的權限名稱,例如:

```
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,BLUETOOTH
```

---
</details>

**注意! : 專案資料夾的主程式必須是 main.py 否則會編譯失敗**

最後插上 Android 裝置並執行
```
buildozer android debug deploy run
```
注意: 第一次build時會連Android需要的NDK之類的大包也一起編譯,需要蠻長的時間2-3小時

編譯完後的 android .apk檔會放在專案資料夾內的 bin 資料夾底下
![android_app.png](https://i.imgur.com/6DUFU1r.png)

[使用 adb工具安裝apk, adb logcat 排查debug](https://shengyu7697.github.io/android-adb/)
在 adb logcat 只偵錯python訊息:
```
adb logcat -s python
```

<details> <summary>地雷:adb logcat 發現 lxml錯誤 </summary>

使用lxml模組
地雷:
- pip install lxml 仍跳出Module not found
- 複製 .venv 下的 lxml包到專案資料夾後錯誤
```
03-17 19:56:38.997  3960  4000 I python  :  ImportError: cannot import name 'etree' from 'lxml' (/data/data/org.test.myapp/files/app/./lxml/__init__.pyc)
03-17 19:56:38.997  3960  4000 I python  : Python for android ended.
```
解決: 試著pip uninstall lxml,但保留專案資料夾內的lxml包,相同錯誤
```
03-17 20:10:09.214  4188  4229 I python  :  ImportError: cannot import name 'etree' from 'lxml' (/data/data/org.test.myapp/files/app/./lxml/__init__.pyc)
03-17 20:10:09.214  4188  4229 I python  : Python for android ended.
```
=> workaround : 改用 bs4 模組(BeautifulSoup)
[kivy 沒支援目前版本(4.9.2)的 lxml 的 alternative 方案 ＝》beautifulSoup, xml2dict,  pyquery .](:/a383e72d8b8c486a9ee833164c750c93)

---
</details>

<details> <summary> 地雷:adb logcat 發現  Module Not Found : bs4 </summary>

adb logcat 發現錯誤 Module Not Found如下:
```
03-17 19:45:34.327  3937  3973 I python  :  ModuleNotFoundError: No module named 'lxml'
03-17 19:45:34.327  3937  3973 I python  : Python for android ended.
```
解決: 
- X) pip install [module名稱] (仍然跳Module Not found)
- O) 把模組從已安裝的地方複製到專案資料夾下(例如. 把虛擬環境已安裝的包/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試/.venv/lib/python3.9/site-packages/bs4複製到專案資料夾)

地雷:上述動作之後adb logcat仍跳出錯誤crash
03-17 19:24:23.230  3880  3962 I python  :  
```
bs4.FeatureNotFound: Couldn't find a tree builder with the features you requested: html5lib. Do you need to install a parser library?
03-17 19:24:23.230  3880  3962 I python  : Python for android ended.
```
解法: 不使用 soup = BeautifulSoup(html_doc, 'html5lib') 改用內建的 html.parser 
```
 soup = BeautifulSoup(html_doc, 'html.parser')
```

---																		</details>


<details> <summary>android 無法呼叫python 錯誤,不能用 subprocess.Popen(["python","auto_predictor.py"])</summary>
2023.03.17 21:03
import auto_predictor 並且在程式碼執行 
import subprocess
        proc_autopredictor = subprocess.Popen(["python","auto_predictor.py"])
出現錯誤
```
03-17 21:01:48.094  3996  4081 I python  :    File "/Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試_android/基本apk專案資料夾/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/python3/armeabi-v7a__ndk_target_21/python3/Lib/subprocess.py", line 1821, in _execute_child
03-17 21:01:48.095  3996  4081 I python  :  FileNotFoundError: [Errno 2] No such file or directory: 'python'
03-17 21:01:48.095  3996  4081 I python  : Python for android ended.
```

---
</details>

<details> <summary>android 背景執行 service的方法 </summary>
[關於android 的 Service](https://xnfood.com.tw/android-service/)

問題:
[How to keep kivy service running in background in Android (service still run when switch to other App or lock the screen)?](https://stackoverflow.com/questions/63218114/how-to-keep-kivy-service-running-in-background-in-android-service-still-run-whe)

原因:
[android 背景執行 service ](https://python-for-android.readthedocs.io/en/latest/services/)
不推薦的舊方法:[Building a background application on android with Kivy.](https://blog.kivy.org/2014/01/building-a-background-application-on-android-with-kivy/)
影片教學:
[Creating an Android Background Service in Kivy Application](https://www.youtube.com/watch?v=f57ItZCtliM)

---


1. 在main.py的繼承App的Myapp(App)內
加入 start_service() 和 on_start(),android 的背景執行service 要加在 on_start() 才能正常運作 
```
    @staticmethod
    def start_service():
        print("start_service執行中")
        from jnius import autoclass
        service = autoclass("org.test.myapp.ServiceCamerapredictor")
        mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
        argument = ""
        service.start(mActivity, argument)
        return service
        

    def on_start(self):
        from kivy import platform
        #from multiprocessing.dummy import Process
        if platform == "android":
            print("on_start已執行")
            self.start_service()
```
其中   `service = autoclass("org.test.myapp.ServiceCamerapredictor")`
的 `org.test.myapp` 是對應 buildozer.spec 內的
```
# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test
```
而 ServiceCamerapredictor 是固定 Service 加上第一個字大寫的 service name, service name對應的是buildozer.spec內的
```
# (list) List of service to declare
services = Camerapredictor:myservice.py
```

2. 在另一個檔案 myservice.py加入
```
from jnius import autoclass
import auto_predictor
PythonService = autoclass("org.kivy.android.PythonService")
PythonService.mService.setAutoRestartService(True)

while True:
    print("service running執行中......")
    try:
        import multiprocessing as mp
        proc_autopredictor = mp.process(target=auto_predictor.main())
        proc_autopredictor.daemon = True
        proc_autopredictor.start()
        #proc_autopredictor.join()
    except Exception as e:
        print(e)
```

3. 在 buildozer.spec
分別修改
在 requirements 加入 pyjnius
```
# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,tqdm,bs4,requests,urllib3,openssl,idna,chardet,pyjnius
```
在 service 加入 [myservice]:[service file path]
例如. Camerapredictor:myservice.py
```
# (list) List of service to declare
services = Camerapredictor:myservice.py
```

4. 不要複製 jnius 包到專案資料夾

---

</details>


<details> <summary> kivy 在不同的頁面資料溝通</summary>

[Use Properties from different classes and screens in KIVY | Kivy Tutorial |](https://www.youtube.com/watch?v=DDAV0T2s2PI)


---

</details>

<details> <summary> 地雷: ModuleNotFoundError: No module named 'android'</summary>

在 PC 端沒有"android",但是在android執行app時會是正常運作的, import android 只會在 android 端作用
參考: [how to import android in python script](https://stackoverflow.com/questions/14709525/how-to-import-android-in-python-script)

You can't install the android module to my knowledge. It exists only on an android Tablet or Phone. So if you run the code on an Android device you don't throw an error. But running it on the PC does throw an Error.

I would recommend using the following code to prevent the error:

import android
from kivy.utils import platform
```
if(platform == 'android'):
    droid = android.Android()
```

---

</details>

<details> <summary>地雷：存取檔案時出現錯誤exposed beyond app through ClipData.Item.getUri </summary>
[exposed beyond app through ClipData.Item.getUri](https://stackoverflow.com/questions/48117511/exposed-beyond-app-through-clipdata-item-geturi)

For sdk 24 and up, if you need to get the Uri of a file outside your app storage you have this error. 
@eranda.del solutions let you change the policy to allow this and it works fine.

However if you want to follow the google guideline without having to change the API policy of your app you have to use a FileProvider.

At first to get the URI of a file you need to use FileProvider.getUriForFile() method:
```
Uri imageUri = FileProvider.getUriForFile(
            MainActivity.this,
            "com.example.homefolder.example.provider", //(use your app signature + ".provider" )
            imageFile);
```

Then you need to configure your provider in your android manifest :

```
<application>
  ...
     <provider
        android:name="android.support.v4.content.FileProvider"
        android:authorities="com.example.homefolder.example.provider"
        android:exported="false"
        android:grantUriPermissions="true">
        <!-- ressource file to create -->
        <meta-data
            android:name="android.support.FILE_PROVIDER_PATHS"
            android:resource="@xml/file_paths">  
        </meta-data>
    </provider>
</application>
```

(In "authorities" use the same value than the second argument of the getUriForFile() method (app signature + ".provider"))

And finally you need to create the ressources file: "file_paths". This file need to be created under the res/xml directory (you probably need to create this directory too) :

```
<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-path name="external_files" path="." />
</paths>
```

The solution provided by Brendon is the correct one but it's not copy-paste ready, you need to check if it suits your needs, for ex. `<external-path ...`  is used when you want Environment.getExternalStorageDirectory(). and use `<files-path ...`  if you need Context.getFilesDir(). You better check official docs first: developer.android.com/reference/android/support/v4/content/… – 
Kirill Karmazin
 Oct 10, 2018 at 19:53


---

</details>

<details> <summary>地雷: 執行apk閃退出現錯誤 ClassNotFoundException: Didn't find class "android.support.v4.content.FileProvider" after androidx migration </summary>

[ClassNotFoundException: Didn't find class "android.support.v4.content.FileProvider" after androidx migration](https://stackoverflow.com/questions/50624510/classnotfoundexception-didnt-find-class-android-support-v4-content-fileprovid)
原因:
```
Based on the stack trace, perhaps you are still using the old package name in the `<provider>` element in the manifest.
```
解法:
```
What to do, find the android.support.v4.FileProvider in your `<provider>` in AndroidManifest.xml.

Change it to androidx.core.content.FileProvider
```
---

(https://www.pyfield.com/blog/?id=20)

---

</details>



---
[回頁首](#頁首)
## p4a (build android apk 工具)
python for android
參考網站:

[Python for Android 踩雷心得](https://medium.com/@k1992313/python-for-android-踩雷心得-f07ac9c106ac)
[kivy在android7以上版本应用FileProvider](https://www.pyfield.com/blog/?id=20)

#### Installing p4a

<details> <summary>安裝  p4a </summary>

參考網站: [python for android-Quickstart](https://python-for-android.readthedocs.io/en/latest/quickstart/)
p4a is now available on Pypi, so you can install it using pip:
```
pip install python-for-android
```
#### Installing Dependencies

On macOS:
```
brew install autoconf automake libtool openssl pkg-config
brew tap homebrew/cask-versions
brew install --cask homebrew/cask-versions/adoptopenjdk8
```
---

</details>

### 安裝Android NDK  和 Andoid SDK, 並設定環境變數

<details> <summary> 安裝Android NDK  和 Andoid SDK, 並設定環境變數 </summary>
- 參考網站:[Python for Android-Getting Started](https://python-for-android.readthedocs.io/en/latest/quickstart/)

## Installing Android SDK

You need to download and unpack the Android SDK and NDK to a directory (let’s say $HOME/Documents/):

- [Android SDK](https://developer.android.com/studio/index.html)
- [Android NDK](https://developer.android.com/ndk/downloads/index.html)

For the Android SDK, you can download ‘just the command line tools’. When you have extracted these you’ll see only a directory named tools, and you will need to run extra commands to install the SDK packages needed.

For Android NDK, note that modern releases will only work on a 64-bit operating system. The minimal, and recommended, NDK version to use is r25b:

- Go to [ndk downloads page](https://developer.android.com/ndk/downloads/)
- Windows users should create a virtual machine with an GNU Linux os installed, and then you can follow the described instructions from within your virtual machine.

### Platform and build tools

First, install an API platform to target. The recommended *target* API level is 27, you can replace it with a different number but keep in mind other API versions are less well-tested and older devices are still supported down to the recommended specified *minimum* API/NDK API level 21:
```
$SDK_DIR/tools/bin/sdkmanager "platforms;android-27"
```
Second, install the build-tools. You can use $SDK_DIR/tools/bin/sdkmanager --list to see all the possibilities, but 28.0.2 is the latest version at the time of writing:
```
$SDK_DIR/tools/bin/sdkmanager "build-tools;28.0.2"
```
### Configure p4a to use your SDK/NDK

Then, you can edit your ~/.bashrc or other favorite shell to include new environment variables necessary for building on android:
```
# Adjust the paths!
export ANDROIDSDK="$HOME/Documents/android-sdk-27"
export ANDROIDNDK="$HOME/Documents/android-ndk-r23b"
export ANDROIDAPI="27"  # Target API version of your application
export NDKAPI="21"  # Minimum supported API version of your application
export ANDROIDNDKVER="r10e"  # Version of the NDK you installed
```
You have the possibility to configure on any command the PATH to the SDK, NDK and Android API using:
```
- --sdk-dir PATH as an equivalent of $ANDROIDSDK
- --ndk-dir PATH as an equivalent of $ANDROIDNDK
- --android-api VERSION as an equivalent of $ANDROIDAPI
- --ndk-api VERSION as an equivalent of $NDKAPI
- --ndk-version VERSION as an equivalent of $ANDROIDNDKVER
```
---

</details>

### Usage (未完成)
<details> <summary>Usage </summary>

參考網站:[Python for Android 踩雷心得](https://medium.com/@k1992313/python-for-android-踩雷心得-f07ac9c106ac)

重要的幾項參數
- ndk_dir, sdk_dir分別指向android ndk和sdk的位置，其中sdk可用sdkmanager安裝特定版本的SDK，而NDK請到android的官網尋找適當的版本。此例是使用SDK29, NDK 17c編譯而成。
- requirements為需要打包的套件，我所知目前支援的套件有numpy, matplotlib, cryptography, usb4a, pyjnius，pyserial尚待確認。
- arch 為設定目標平台
- release為是否釋出之版本
 其他像whitelist、blacklist有空要再了解一下，似乎可避免打包後檔案過肥的問題
 執行完成後，會在當下目錄產生APK檔，即可安裝入android系統內。

```
p4a apk --private /Users/2020mac01/Documents/測量與空間資訊_project/xml_parser練習/kivy_測試_android/basic_apk_資料夾/ \
--package=org.test.myapp \
--name "MY CAMERA" \
--version 0.1 \
--bootstrap=sdl2 \
--requirements=python3,kivy,android,pyjnius,plyer,pillow,bs4,requests,urllib3,idna,chardet,lxml,sdl2,pyobjus,tqdm \
--sdk_dir=/Users/2020mac01/Documents/Android_project/ANDROID_SDK/ \
--ndk_dir=/Users/2020mac01/Documents/Android_project/ANDROID_NDK/ \
--arch=arm64-v8a \
--arch=armeabi-v7a \
--add-aar=/Users/2020mac01/Documents/python_projects/basic_apk_project/support-v4-24.1.1.aar  \
--permission android.permission.WRITE_EXTERNAL_STORAGE \
--permission android.permission.READ_EXTERNAL_STORAGE \
--permission android.permission.WRITE_EXTERNAL_STORAGE  \
--permission android.permission.CAMERA \
--permission android.permission.INTERNET \
--service=Camerapredictor:myservice.py 
```

---

</details>

### Build failed
- 地雷: link name too long
參考網站: [ValueError : Linkname is too long](https://stackoverflow.com/questions/30665420/valueerror-linkname-is-too-long)

<details> <summary> 地雷: link name too long </summary>
問題關鍵：

```
Maybe check to see if your python-for-android folder is inside your project directory (/home/sahil/Desktop/kivy)?

I was getting this error too until I moved the python-for-android folder outside the directory with my kivy code and whatnot. Then I was able to build the apk successfully.
```

解決: 縮短資料夾路徑 (把資料夾移到外層,讓路徑縮短)

---

</details>


### 閃退,安裝失敗

- 地雷: Failure [INSTALL_FAILED_NO_MATCHING_ABIS: Failed to extract native libraries, res=-113]

<details> <summary>地雷: Failure [INSTALL_FAILED_NO_MATCHING_ABIS: Failed to extract native libraries, res=-113]</summary>

參考網站:[Failure [INSTALL_FAILED_NO_MATCHING_ABIS: Failed to extract native libraries, res=-113]](https://blog.csdn.net/Leafage_M/article/details/86675699)
```
由于安装的APP中使用了与当前CPU架构不一致的native libraries,所以导致报错，因为现在绝大多数的智能手机还都是采用ARM架构的，虽然android是支持ARM和x86架构，但是它们的指令集是有差别的，APP在开发的时候使用的是ARM的本地库，而我们在用AVD创建模拟器的时候使用的是x86的CPU，因此导致报错。所以，如果APP是在x86架构下编译的我们就创建x86cpu的模拟器，如果APP是在ARM架构编译的我们就创建ARMcpu的模拟器。
问题已经很清楚了，是当前的app使用了native libraries与模拟器的CPU架构不一致所导致的，而genymotion模拟器默认创建的只支持x86架构而不支持arm架构，这样看来这个app使用了支持arm架构的一些库，所以在x86上会无法安装。事实就是源码中使用了.so文件，当一个应用安装在设备上，只有该设备支持的CPU架构对应的.so文件会被安装。所以对应的arm部分文件无法安装从而导致安装失败。

```
解決: p4a 指令使用 --arch 指定對應的arm 或 x86架構

---

</details>

build 成功,但閃退
- 地雷: Entrypoint not found (.py), abort.


<details> <summary>地雷:  Entrypoint not found (.py), abort.</summary>
執行命令:

```
p4a apk --private $HOME/Documents/python_projects/basic_apk_project \
--package=org.test.myapp \
--name "MY CAMERA" \
--version 0.1 \
--bootstrap=sdl2 \
--requirements=python3,kivy,android,pyjnius,plyer,pillow,bs4,requests,urllib3,idna,chardet,lxml,sdl2 \
--sdk_dir=/Users/2020mac01/Documents/Android_project/ANDROID_SDK/ \
--ndk_dir=/Users/2020mac01/Documents/Android_project/ANDROID_NDK/ \
--arch=arm64-v8a \
--arch=armeabi-v7a \
--add-aar=/Users/2020mac01/Documents/python_projects/basic_apk_project/support-v4-24.1.1.aar  \
--permission android.permission.WRITE_EXTERNAL_STORAGE \
--permission android.permission.READ_EXTERNAL_STORAGE \
--permission android.permission.WRITE_EXTERNAL_STORAGE  \
--permission android.permission.CAMERA \
--permission android.permission.INTERNET \
--service=Camerapredictor:myservice.py 
```

問題: 
build 完 code,裝到 Android,執行時閃退: 用 `./adb logcat -s python` 指令查看錯誤訊息
```
05-08 18:33:49.423  5358  5401 I python  : Entrypoint not found (.py), abort.
```
(X)參考網站: [Kivy app crashing on Android device (Error: Entrypoint not found)](https://stackoverflow.com/questions/58574074/kivy-app-crashing-on-android-device-error-entrypoint-not-found)
(O) --service=Camerapredictor:myservice.py 需要用對路徑,參考網址 [python for android 的 背景運行service](https://python-for-android.readthedocs.io/en/latest/services/)
(O)用 hello world 版本的程式排查, 發現是 .venv **隱藏資料夾**移除後,在build code後,裝在Android模擬器(或裝置)就可正常開啟程式

---

</details>

未使用
<details> <summary> kivy 移除開頭黑畫面,減少讀取時間</summary>

[Remove Black Screen At Startup and Reduce the Loading Time in Kivy {/Android}](https://www.youtube.com/watch?v=Y9t-dBQ0a9w&t=191s)

---

</details>
