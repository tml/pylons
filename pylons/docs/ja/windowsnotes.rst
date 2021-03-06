.. Windows Notes

.. _windows_notes:

=======================
Windows における注意点
=======================

.. Python scripts installed as part of the Pylons install process will be
.. put in the ``Scripts`` directory of your Python installation,
.. typically in ``C:\Python24\Scripts``. By default on Windows, this
.. directory is not in your ``PATH``; this can cause the following error
.. message when running a command such as ``paster`` from the command
.. prompt:

Pylons のインストール過程でインストールされる Python スクリプト群は、
Python インストールディレクトリの ``Scripts`` ディレクトリ（標準では
``C:\Python24\Scripts`` ）におかれます。Windows のデフォルトでは、この
ディレクトリは ``PATH`` に含まれていません。そのため、 ``paster`` のよ
うなコマンドを実行した際に、次のようなエラーがコマンドプロンプトに表示
される可能性があります。

.. code-block:: text

	C:\Documents and Settings\James>paster
	'paster' is not recognized as an internal or external command,
	operable program or batch file.

.. To run the scripts installed with Pylons either the full path must be specified:

Pylons でインストールされたスクリプトを実行するためには、フルパスで指定するか、

.. code-block:: text

	C:\Documents and Settings\James>C:\Python24\Scripts\paster
	Usage: C:\Python24\Scripts\paster-script.py COMMAND
	usage: paster-script.py [paster_options] COMMAND [command_options]

	options:
	  --version         show program's version number and exit
	  --plugin=PLUGINS  Add a plugin to the list of commands (plugins are Egg
			    specs; will also require() the Egg)
	  -h, --help        Show this help message
	
	... etc ...
	
.. or (the preferable solution) the ``Scripts`` directory must be
.. added to the ``PATH`` as described below.

（より好ましい解決方法として、）以下に示すように ``Scripts`` ディレクト
リを ``PATH`` に追加する必要があります。


.. For Win2K or WinXP

Windows 2000 または Windows XP の場合
--------------------------------------

.. #. From the desktop or Start Menu, right click My Computer and click Properties.
.. #. In the System Properties window, click on the Advanced tab.
.. #. In the Advanced section, click the Environment Variables button. 
.. #. Finally, in the Environment Variables window, highlight the path variable in the Systems Variable section and click edit. Add or modify the path lines with the paths you wish the computer to access. Each different directory is separated with a semicolon as shown below:

#. デスクトップかスタートメニューで「マイ コンピュータ」を右クリックし、「プロパティ」を選択してください。
#. 「システムのプロパティ」ウィンドウで「詳細設定」タブを選択してください。
#. 「詳細設定」項目で「環境変数」のボタンをクリックしてください。
#. 最後に「環境変数」のウィンドウにおいて、「システム環境変数」の中の path 変数の項目をハイライトさせ、「編集」をクリックしてください。コンピュータにアクセスしてほしいパスを path の行に追加するか、行を編集してください。各ディレクトリは、以下に示すようにセミコロンで区切ります。

.. code-block:: text

	C:\Program Files;C:\WINDOWS;C:\WINDOWS\System32
      
.. #. Add the path to your scripts directory:

#. スクリプトディレクトリへのパスを追加してください。

.. code-block:: text

	C:\Program Files;C:\WINDOWS;C:\WINDOWS\System32;C:\Python24\Scripts
	
.. See `Finally`_ below.

`最後に`_ を読んでください。


	
.. For Windows 95, 98 and ME

Windows 95, 98, ME の場合
--------------------------

.. Edit ``autoexec.bat``, and add the following line to the end of the file:

``autoexec.bat`` を編集し、ファイルの最後に以下の行を追加してください。


.. code-block:: bash

	set PATH=%PATH%;C:\Python24\Scripts

.. See `Finally`_ below.

`最後に`_ を読んでください。

.. Finally

最後に
-------

.. Restarting your computer may be required to enable the change to
.. the ``PATH``. Then commands may be entered from any location:


``PATH`` の変更を有効にするためには、コンピュータの再起動が必要かも知れ
ません。これにより、コマンドは任意の場所から実行できるようになります。

.. code-block:: text

	C:\Documents and Settings\James>paster
	Usage: C:\Python24\Scripts\paster-script.py COMMAND
	usage: paster-script.py [paster_options] COMMAND [command_options]

	options:
	  --version         show program's version number and exit
	  --plugin=PLUGINS  Add a plugin to the list of commands (plugins are Egg
			    specs; will also require() the Egg)
	  -h, --help        Show this help message
	
	... etc ...

.. All documentation assumes the ``PATH`` is setup correctly as described above.

すべてのドキュメントにおいて、このように ``PATH`` が適切に設定されてい
ることを想定しています。
