# フロントシステム セットアップ

- 目次
    - 
    

## 必要物品

- [ ]  Raspberry Pi4×2個(メインとなるものと、外に設置するもの)
- [ ]  microSDカード×2個
- [ ]  マウス×1個
- [ ]  キーボード×1個
- [ ]  モニター×1個
- [ ]  NFCカードリーダー×2個
- [ ]  switch bot×1個
- [ ]  switch botハブミニ×1個
- [ ]  ACアダプタ(type C)×2個
- [ ]  Micro HDMIケーブル×1個
- [ ]  スピーカー×2個

## 設定手順

### メインとなるRaspberry Pi設定項目

1. [Raspberry Piの設定](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
2. [Dockerによるデータベース作成](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
3. [アプリのクローン・設定](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
4. [Slack設定](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
5. [扉開閉スイッチを動かすアプリ](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
6. [Apacheによるデプロイ](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
7. [モーターのセット方法](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)

### メイン以外(外に設置する物)のRaspberry Pi設定項目

1. [Raspberry Piの設定](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
2. [アプリのクローン・設定](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
3. [扉開閉スイッチを動かすアプリ](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)
4. [アプリケーションの自動起動](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)

## 最初に

### ターミナルについて

- これからRaspberry piのセットアップ手順を説明していきますが、そこでターミナルを多用します。
- ターミナルの開き方は、
    1. デスクトップの左上にあるメニューバーを開きます。
    2. メニューからアクセサリを選択します。
    3. 1. 「LXTerminal」または「ターミナル」をクリックし開きます。

### パッケージのインストール時の注意点

- ターミナルにて、以下のコマンドを入力し、実行したとします。

```
sudo pip3 install パッケージ名
```

- インストールするパッケージによっては、以下のような文章が出力されることがあります。

```
WARNING: The following packages will be installed:
    package1
    package2

    ...
Proceed (y/n)?
```

- この文章はパッケージのインストールに関する注意を示し、続行するかどうかをユーザに確認するためのものです。
- この文章が出力された際は、ターミナルにて「y」と入力してください。インストールが始まります。

## Raspberry Piの設定

### OSインストール

1. Raspberry Pi OSをダウンロードするためのWebサイトを開いてください。
2. [**https://www.raspberrypi.com/software/**](https://www.raspberrypi.com/software/) より、Download for WindowsをクリックしてRaspberry Pi Imagerをダウンロード、インストールしてください。
3. インストールが完了したRaspberry Pi Imagerを起動し、一番左側の「OSを選ぶ」をクリックします。
4. 「Raspberry Pi OS (32-bit)」を選択します。
5. その後、中央の「ストレージを選ぶ」をクリックし、書き込み先のSDカードを選択してください。
6. 左側の「書き込む」をクリックして、ダウンロードと書き込みを開始してください。

### 初期セットアップ

1. SDカードにOSを書き込んだら、Raspberry Piを起動し、初期セットアップを開始します。
2. 最初に言語の設定画面が表示されます。"Japanese"を選択してNextをクリックします。
3. 次に、ユーザーの設定画面が表示されます。"Enter username"に"pi"を入力し、"Enter password"および"Confirm password"に"raspberry"を入力してください。
4. 次に、ディスプレイの設定画面が表示されます。"Reduce the size of the desktop on this monitor”はオフのままで、Nextをクリックします。
5. 次に、Wi-Fiの設定画面が表示されます。使用可能なWi-Fiネットワークを選択して、パスワードを入力してください。入力が完了したら、Nextをクリックします。
6. 次に、ネットワークのアップデート画面が表示されます。"Skip"をクリックします。
7. 最後に、セットアップ完了画面が表示されます。"Restart"をクリックして、Raspberry Piを再起動して設定を反映させてください。

### SSHの有効化

1. Raspberry Pi側で、設定をクリックし、"Raspberry Piの設定"を選択します。
2. "インターフェイス"タブを選択し、"SSH"をONにして、OKをクリックします。
3. 次に、Raspberry Pi側でターミナルを開き以下のコードを実行してIPアドレスを確認、メモしておきます。

```
hostname -I
```

1. PC側で、Raspberry Piと接続します。
2. SSHを使ってRaspberry Piを操作するために、PC側でコマンドプロンプト(ターミナル)を開き、以下のコマンドを入力します。

```
ssh pi@192.168*** **
```

*"****"には、上記でメモしたRaspberry PiのIPアドレスを入力してください。

1. 接続を続けてもよいか聞かれたら、yesと入力しEnterを押し、Raspberry Piのパスワードを入力て下さい。
2. 先ほど設定したパスワードを入力し、PCからRaspberry Piを操作することができます。

### 日本語入力設定

1. Raspberry Piを起動後、ターミナルを開き、以下のコマンドを入力して実行します。

```
sudo apt install -y fcitx-mozc
```

1. インストールが完了したら、以下のコマンドを入力してRaspberry Piを再起動します。

```
reboot
```

1. これで日本語入力ができるようになります。

## Dockerによるデータベース作成

<aside>
💡 ※メインとなるRaspberry piのみ、この項目を行ってください。それ以外のRaspberry piは個別でデータベースを持つ必要がないためこの項目は不要です。次の[アプリのクローン・設定](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)から手順に沿って設定を進めてください。

</aside>

### Dockerのインストール

1. ターミナルを開き、以下のコマンドを実行します。
    
    ```
    sudo apt install docker.io
    ```
    
2. Dockerコマンドを実行可能にするため、以下のコマンドを実行します。
    
    ```
    sudo usermod -aG docker pi
    ```
    
3. 再起動します。
    
    ```
    reboot
    ```
    

### Docker Composeのインストール

1. ターミナルを開き、以下のコマンドを実行します。
    
    ```
    sudo apt install docker-compose -y
    ```
    
2. Docker Composeの最新版へバージョンアップするため、以下のコマンドを実行します。
    
    ```
    sudo pip3 install --upgrade docker-compose
    ```
    
3. 再起動します。
    
    ```
    reboot
    ```
    

### Dockerフォルダの設定

1. 以下のコマンドをターミナルで実行し、docker_settingというフォルダを作成します。
    
    ```
    mkdir /home/pi/docker_setting
    ```
    
2. 以下のコマンドをターミナルで実行し、作成したフォルダに移動します。
    
    ```
    cd /home/pi/docker_setting
    ```
    
3. 以下のコマンドをターミナルで実行し、docker-compose.ymlとinit-mysql.shという名前のファイルを作成します。
    
    ```
    touch docker-compose.yml
    touch init-mysql.sh
    ```
    
4. 以下のコマンドをターミナルで実行。dockerという名前のフォルダを作成し、その中にdbという名前のフォルダを作成します。
    
    ```
    mkdir /home/pi/docker_setting/docker
    mkdir /home/pi/docker_setting/docker/db
    ```
    
1. 以下のコマンドをターミナルで実行。dbフォルダ内にmy.cnfという名前のファイルを作成し、dataとsqlという名前のフォルダを作成します。
    
    ```
    cd /home/pi/docker_setting/docker/db
    touch my.cnf
    mkdir /home/pi/docker_setting/docker/db/data
    mkdir /home/pi/docker_setting/docker/db/sql
    ```
    
2. 以下のコマンドをターミナルで実行。sqlフォルダ内にinit.sqlという名前のファイルを作成し、init-database.shという名前のファイルを作成します。
    
    ```
    cd /home/pi/docker_setting/docker/db/sql
    touch init.sql
    touch init-database.sh
    ```
    

### フォルダ構造

1. 現時点でのDockerを設定するフォルダの構造は以下のようになっています。

```
docker_setting
|-docker-compose.yml
|-init-mysql.sh
|-docker
   |-db
      |-my.cnf
      |-sql
      |  |-init-database.sh
      |   |-init.sql
      |-data #空のフォルダ
```

### Dockerの設定

1. 以下のコマンドをターミナルで実行します。

```
nano /home/pi/docker_setting/docker-compose.yml
```

1. docker-compose.ymlという設定ファイルが開くので、 そこに以下のコードを記述してください。

```
version: "3"
services:
  db:
    image: hypriot/rpi-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: mypassword
      MYSQL_DATABASE: exit_entrance_management
      MYSQL_USER: root
      MYSQL_PASSWORD: mypassword
    command: mysqld --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    volumes:
        - ./docker/db/data:/var/lib/mysql
        - ./docker/db/my.cnf:/etc/mysql/conf.d/my.cnf
        - ./docker/db/sql:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
```

`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1. 以下のコマンドをターミナルで実行します。

```
nano /home/pi/docker_setting/init-mysql.sh
```

1. [init-mysql.sh](http://init-mysql.sh/) ファイルが開くため、以下のコードを記述してください。

```
#!/bin/sh
docker-compose exec db bash -c "chmod 0775 docker-entrypoint-initdb.d/init-database.sh"

docker-compose exec db bash -c "./docker-entrypoint-initdb.d/init-database.sh"
```

`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1. 以下のコマンドをターミナルで実行します。

```
nano /home/pi/docker_setting/docker/db/my.cnf
```

1. my.cnf ファイルが開くため、以下のコードを記述してください。

```
[mysqld]
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

[client]
default-character-set=utf8mb4
```

`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1. 以下のコマンドをターミナルで実行してください。

```
nano /home/pi/docker_setting/docker/db/sql/init.sql
```

1. init.sqlが開くため、以下のコードを記述してください。

```
CREATE DATABASE IF NOT EXISTS `exit_entrance_management` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `exit_entrance_management`;

---- create tables ----
CREATE TABLE IF NOT EXISTS `staff` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `name` VARCHAR(30) NOT NULL,
 `login_id` VARCHAR(12) NOT NULL,
 `password` VARCHAR(255) NOT NULL,
 `authority` TINYINT(1),
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `resident` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `name` VARCHAR(30) NOT NULL,
 `number` INT(5) NOT NULL,
 `number_people` INT(2) NOT NULL,
 `going_to_alone` VARCHAR(30) NOT NULL,
 `card_id` VARCHAR(30) NOT NULL,
 `reason` VARCHAR(20),
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `card_record` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `datetime` DATETIME NOT NULL,
 `type` VARCHAR(30) NOT NULL,
 `idm` VARCHAR(20) NOT NULL,
 `staff_name` VARCHAR(255),
 `reason` VARCHAR(255),
 `update_time` VARCHAR(255),
 `first_time` VARCHAR(255),
 `return_id` VARCHAR(255),
 `return_complete` TINYINT(1) DEFAULT 0,
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `return_data` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `datetime` DATETIME NOT NULL,
 `type` VARCHAR(30) NOT NULL,
 `idm` VARCHAR(20) NOT NULL,
 `staff_name` VARCHAR(255),
 `reason` VARCHAR(255),
 `update_time` VARCHAR(255),
 `first_time` VARCHAR(255),
 `go_id` VARCHAR(255),
 `resident_idm` VARCHAR(255),
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `resident_mail` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `resident_id` INT(11) NOT NULL,
 `reason` VARCHAR(255),
 `staff_name` VARCHAR(255) NOT NULL,
 `keep_mail_day` DATE NOT NULL,
 `status` VARCHAR(255) NOT NULL,
 `check_staff` VARCHAR(255),
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `space_data` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `space_name` VARCHAR(20) NOT NULL,
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `space_rental` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `staff_or_resident` VARCHAR(10) NOT NULL,
 `date_time` DATETIME NOT NULL,
 `end_time` DATETIME NOT NULL,
 `reason` VARCHAR(255),
 `user_id` INT(11) NOT NULL,
 `start_time` DATETIME NOT NULL,
 `space_name` VARCHAR(20),
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `staff_card` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `name` VARCHAR(30) NOT NULL,
 `card_id` VARCHAR(30) NOT NULL,
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `remarks` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `remark` VARCHAR(100) NOT NULL,
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `data_check` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
 `datetime` DATETIME NOT NULL,
 `idm` VARCHAR(255) NOT NULL,
 `scan_card_name` VARCHAR(255),
 PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

---- insert initial data ----
INSERT INTO staff (name, login_id, password, authority)
VALUES ('TEST STAFF', '1111', '$2b$12$j1HOjS6r2HOgDShxEp4/WOkbhTJsONlzkwwdnBYUBGXu2kOBMHGJO', 1);

INSERT INTO card_record (datetime, type, idm)
VALUES ('2000-01-01 00:00:00', 'return', 'test');

```

`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1. 以下のコマンドをターミナルで実行します。

```
nano /home/pi/docker_setting/docker/db/sql/init-database.sh
```

1. init-database.shファイルが開くため、以下のコードを記述してください。

```
#!/usr/bin/env bash
#wait for the MySQL Server to come up
#sleep 90s

#run the setup script to create the DB and the schema in the DB
mysql -u root -pmypassword exit_entrance_management < "/docker-entrypoint-initdb.d/init.sql"
```

`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

### コンテナのビルドと実行

<aside>
💡 ※以下のコマンドを実行し、エラーが出る場合は再起動して再度試して下さい。

</aside>

1. ターミナルを開き、以下のコマンドを入力し、docker_settingフォルダに移動します。

```
cd /home/pi/docker_setting
```

1. 以下のコマンドをターミナルで入力し、MySQLコンテナをバックグラウンドで起動します。

```
docker-compose up -d
```

1. 一度以下のコマンドをターミナルで実行し、再起動します。

```
reboot
```

1. ターミナルを開き、以下のコマンドを入力し、docker_settingフォルダに移動します。

```
cd /home/pi/docker_setting
```

1. 以下のコマンドをターミナルで入力し、init-mysql.shファイルを実行して初期設定を行います。

```
bash /home/pi/docker_setting/init-mysql.sh
```

1. 以下のコマンドをターミナルで入力し、MySQLコンテナに入ります。

```
docker exec -it docker_setting_db_1 /bin/bash
```

1. 以下のコマンドを実行し、出力されたDockerのIPアドレス(例:172.17.***)をメモします。

```
hostname -i
```

1. 以下のコマンドを入力し、MySQLにログインします。

```
mysql -u root -p
```

1. パスワードを入力します。

```
パスワード: mypassword
```

これで、データベースが起動し、MySQLコンテナ内に入り、データベースにログインできたらDockerによるデータベースの作成は完了です。

`Ctrl + c`を押した後、以下のコードを入力し、もとのターミナルに戻ります。

```
exit
```

## アプリのクローン・設定

### アプリのクローン方法

1. ターミナルで以下のコマンドを順番に実行してください。

```
cd /home/pi
```

```
git clone https://github.com/frontsystem-1/front_system.git
```

1. これでexit_entrance_appというフォルダと必要なファイルをクローンしました。
2. 次にターミナルで以下のコマンドを実行してください。

```
cd /home/pi/exit_entrance_app
```

1. 各アプリのコードを修正します。以下のコマンドをそれぞれ実行し、ファイルを開きます。

```
nano switch_app.py
```

```
nano nfc_reader.py
```

```
nano return_nfc_reader.py
```

1. 上記のコマンドをそれぞれ実行すると、各ファイルのコードが表示されます。その中で、以下の部分を修正していきます。
    
    <aside>
    💡 ※メインのRaspberry Piとメイン以外のRaspberry Piでは入力するコードが違います。
    
    </aside>
    

```
#元のコード
connection = MySQLdb.connect(
host=os.environ['CONTAINER_ID'],
user=os.environ['DB_USER'],
password=os.environ['DB_PASS'],
db=os.environ['DB_NAME'],
charset='utf8',
)
```

- メインのRaspberry piでは、上のコードを以下のように修正してください。

※[メインRaspberry piのDockerのIPアドレス](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)

修正後は`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

```
connection = MySQLdb.connect(
host='#ここに先ほどメモしたメインRaspberry piのDockerのIPアドレスを貼り付け',
user='root',
password='mypassword',
db='exit_entrance_management',
charset='utf8',
)
```

- メイン以外のRaspberry piでは、先ほどのコードを以下の様に修正して下さい。

※[メインのRaspberry piのIPアドレス](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)

```
connection = MySQLdb.connect(
host='#ここに先ほどメモしたメインRaspberry piのIPアドレスを貼り付け',
user='root',
password='mypassword',
db='exit_entrance_management',
charset='utf8',
)
```

## Slack設定

扉開閉アプリでは、扉が開いた際に誰が何時に開けたのかをSlackに通知させます。ここではその設定のためのSlackトークン発行の手順を説明します。

<aside>
💡 ※既にSlackのアカウント、ワークスペースがあることを前提としています。

</aside>

### Slack設定

1. PCで[Slackのウェブサイト](http://slack.com)にアクセスします。
2. 「Sign In」ボタンを押しログインします。
3. 現在使用中のワークスペースを選択します。
4. 「チャンネルを追加する」をクリックし、「新しいチャンネルを作成」を選択します。
5. チャンネルの名前を「exitresident」と入力し、「次へ」をクリックします。
6. そのまま「作成」を押して通知用のチャンネルを新規作成します。
7. メンバーの追加は「後でする」を押してスキップします。

### Slack API設定(トークン発行)

1. [Slack APIのウェブサイト](https://api.slack.com/)にアクセスします。
2. 右上の「Sign In」というボタンをクリックして、Slackのアカウントにログインします。
3. Slack APIのダッシュボードに移動します。左側のメニューの「Your Apps」をクリックします。
4. 「Create New App」をクリックします。
5. 「From scratch」を選択し、App Nameに 「exit_resident」、Pick a workspace to develop your app in:は先ほどチャンネルを作ったワークスペースを選択します。
6. ページの左端のメニューから「OAuth & Permissons」をクリックします。
7. Bot Token Scopesと書いてある項目の下にある 「Add an OAuth Scope」をクリックします。
8. 表示された入力欄に「chat:write」と入力し、Enterキーを押します。
9. ページの上の方にある「Install to Workspace」をクリックします。
10. 「許可する」をクリックします。
11. 表示されたページのOAuth Tokens for Your Workspaceと書いてある項目の下に、Bot User OAuth Tokenとしてトークンが発行されています。
12. このトークンをコピーしメモします→[アプリ設定](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)で使用します。

## 扉開閉スイッチを動かすアプリ

### 必要なライブラリのインストール

1. ターミナルを開き、以下のコマンドでパッケージリストをアップデートします。

```
sudo apt update
```

1. ターミナルにて以下のコマンドを貼り付け、アップデートが必要なパッケージをアップグレードします。

```
sudo apt upgrade
```

1. ターミナルにて下記のコマンドを順番に実行していきます
2. ページ機能用のflask_paginateをインストールます。以下のコマンドをターミナルに貼り付け実行して下さい。

```
sudo pip3 install flask_paginate
```

1. NFCリーダーの制御を行う nfcpy をインストールします。以下のコマンドをターミナルに貼り付け実行して下さい。

```
sudo pip3 install nfcpy
```

1. アプリを正常に起動するために、python-dotenvをインストールします。以下のコマンドをターミナルにはり付け実行して下さい。

```
sudo pip3 install python-dotenv
```

1. データベースを操作するための mysqlclient をインストールします。以下のコマンドをターミナルに貼り付け実行して下さい。

```
sudo pip3 install mysqlclient
```

1. データベース制御のためにMariaDB C Client Libraryをインストールします。以下のコマンドをターミナルに貼り付け実行して下さい。

```
sudo apt-get install libmariadb-dev-compat libmariadb-dev
```

1. 関数の実行時間制限を設ける timeout_decoratorをインストールします。以下のコマンドをターミナルに貼り付け実行して下さい。

```
sudo pip3 install timeout_decorator
```

1. 状態遷移を管理するための transitionsをインストールします。以下のコマンドドをターミナルに貼り付け実行して下さい。

```
sudo pip3 install transitions
```

1. パスワードを暗号化するために Flask-bcrypt をインストールします。以下のコマンドをターミナルに貼り付け実行して下さい。

```
sudo pip3 install Flask-Bcrypt
```

1. NFCリーダーの設定を行います。下記のコマンドをターミナルで実行して下さい。

```
python3 -m nfc
```

1. すると以下の様な二つのコマンドが出てきますので、それを順番にコピーしターミナルに貼り付けて実行して下さい。

<aside>
💡 ※以下のコードは例です。各パソコンで上記のコードを実行し、出現したコマンドで行って下さい。

</aside>

![スクリーンショット 2023-07-03 8.22.02.png](%E3%83%95%E3%83%AD%E3%83%B3%E3%83%88%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%20%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%95%E3%82%9A%206fc4d41cb143460fb87b4740180532fd/%25E3%2582%25B9%25E3%2582%25AF%25E3%2583%25AA%25E3%2583%25BC%25E3%2583%25B3%25E3%2582%25B7%25E3%2583%25A7%25E3%2583%2583%25E3%2583%2588_2023-07-03_8.22.02.png)

この画像のように表示されますので、以下のコードの部分(画像真ん中付近)を順番にターミナルで実行して下さい。

```
sudo sh -c 'echo SUBSYSTEM==\\"usb\\", ACTION==\\"add\\", ATTRS{idVendor}==\\"054c\\", ATTRS{idProduct}==\\"06c1\\", GROUP=\\"plugdev\\" >> /etc/udev/rules.d/nfcdev.rules'
```

```
sudo udevadm control -R
```

以上で必要なライブラリのインストールが完了しました。

1. 最後に以下のコマンドをターミナルで実行し再起動します。

```
reboot
```

### カードリーダ設定

カードリーダーの仕様に関してのファイルを修正していきます。

1. ターミナルにて下記のコマンドを実行します。

```
cd /home/pi/exit_entrance_app
```

1. カードリーダーを設定するためのファイルを開きます。ターミナルにて下記のコマンドを実行して下さい。

```
nano nfc_reader.py
```

1. 開かれたファイル内の下記の部分のコードを修正します。

```
def __init__(self):
            self.idm_data = ''
            #self.card_type = input('go or return')
            self.card_type = 'go'
            self.now_format = ''
            self.last_time = datetime.datetime.now()
            self.error_judgment = ''
```

この、”self.card_type = ‘go’“の部分を、現在設定中のRaspberry piを室内に行くならそのまま、外に置くなら下記のように修正して下さい修正してください。

```
self.card_type = 'return'
```

修正後は`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

### データベース設定

データベース使用に関してのファイルを修正していきます。

1. 以下のコマンドをターミナルで実行します。

```
cd /home/pi/exit_entrance_app
```

1. データベースを操作するためのファイルを開きます。ターミナルにて下記のコマンドを実行して下さい。

```
nano db_use.py
```

1. 開かれたファイル内の下記のコードを修正します。

```
#日時、名前、詳細をslackに通知させる
def notification(day,time,name,nb):
		if cr.error_judgment == 'error':
				print('network error')
				return
		url = "https://slack.com/api/chat.postMessage"
		data = {
		"token":os.environ['TOKEN'],
		"channel":"exitresident",
		"text":"%s %s %s様: 外出%s" % (day,time,name,nb)
		}
		requests.post(url,data=data)
```

このコードの” "token":os.environ['TOKEN'], ”の部分を以下のように書き換えて下さい。

```
"token":'先程取得したSlackのトークン'
#例: 'xoxb-4610993849044-4611014137156-2pTJZhzzP48hBDYARzOyvYf7',
```

修正後は`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

### webページ機能の設定

<aside>
💡 webページの設定となるため、メインとなるRaspberry piでのみ行ってください。

</aside>

1. 以下のコマンドをターミナルで実行し、ファイルを開きます。

```
nano /home/pi/exit_entrance_app/templates/layout.html
```

1. 開かれたファイルの以下のコードを変更します。

```
#変更前
fetch('/' + {{staff_id|tojson}} + '/sign_out', {
        method: 'POST',
         headers: {
          'Content-Type': 'application/json' // リクエストヘッダーのContent-Type
        },
```

```
#変更後
fetch('http://' + '#ここに先ほどメモしたメインRaspberry piのDockerのIPアドレスを貼り付け' + '/' + {{staff_id|tojson}} + '/sign_out', {
        method: 'POST',
         headers: {
          'Content-Type': 'application/json' // リクエストヘッダーのContent-Type
        },
```

修正後は`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

## Apacheによるデプロイ

同Wi-Fi内で、PCやスマートフォンからアプリの画面へアクセスできるように設定します。

<aside>
💡 ※メインとなるRaspberry piでのみ行って下さい。

</aside>

### Apacheのインストール

1. まず、ターミナルを開き、以下のコマンドを実行してApache2をインストールします。

```
sudo apt update
sudo apt install apache2
sudo apt install libapache2-mod-wsgi-py3
```

### アプリケーションの配置

1. 次に、アプリを配置します。以下のコマンドをターミナルで実行して、アプリをApache2のドキュメントルートにコピーします。

```
sudo cp -pR /home/pi/exit_entrance_app/*  /var/www/html/
```

### Apache2の設定変更

1. 設定ファイルを開き、アプリに関する設定を追加します。以下のコマンドをターミナルで実行して下さい。

```
sudo nano /etc/apache2/sites-available/000-default.conf
```

1. 上記コマンドを実行すると、ファイルが開きます。以下の内容をコピーして、DocumentRoot /var/www/htmlと書かれている下に貼り付けます。

```
ServerName example.com
WSGIDaemonProcess switch_app user=pi group=pi threads=5
WSGIScriptAlias / /var/www/html/switch_app.wsgi
<Directory /var/www/html>
    WSGIProcessGroup switch_app
    WSGIApplicationGroup %{GLOBAL}
    WSGIScriptReloading On
    Require all granted
    Options FollowSymLinks
    AllowOverride All
</Directory>
```

修正後は`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

### WSGIファイルの作成

1. 次に、アプリをApache2で実行するためのWSGIファイルを作成します。以下のコマンドをターミナルで実行して下さい。

```
sudo nano /var/www/html/switch_app.wsgi
```

上記コマンドを実行すると、新しいファイルが作成・表示されます。以下の内容をコピーして、貼り付けます。

```
#!/usr/bin/python3
import sys
sys.path.insert(0, '/var/www/html')

from switch_app import app as application

```

貼り付けが完了したら、`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1. 以下のコマンドをターミナルで実行し、設定を有効にします。

```jsx
sudo a2enmod wsgi
```

1. 以下のコマンドを順番にターミナルで実行します。

```
cd /var/www/html
```

```
chmod +x switch_app.py
```

### Apache2の再起動

1. ターミナルにて下記のコードを実行し、Apache2を再起動します。

```
sudo service apache2 restart
```

1. 以下のコマンドをターミナルで実行して、アプリのURLを取得します。

```
	hostname -I
```

表示された’198.168’から始まるIPアドレスをコピーします。

1. 次に、以下のURLをブラウザのURL欄に貼り付け、’/sign_in’を入力してEnterキーを押します。

```
http://<コピーしたIPアドレス>/sign_in
```

ページが表示されれば、アプリに正常にアクセスできるようになります。

## アプリケーションの自動起動

Raspberry Piを起動した際に自動で各アプリケーションが起動するように修正します。

1. 以下のコマンドをターミナルで実行し、設定用のファイルを開きます。

```
nano /home/pi/start_app.py
```

1. 以下のコードを設定用のファイルに貼り付けてください。

<aside>
💡 ※メインとメイン以外のRaspberry piの場合でコードが異なります。

</aside>

- メインRaspberry piの場合

```
#メインRaspberry pi用のコード
import subprocess
import time

def docker_start():
	subprocess.run(['docker','start','docker_setting_db_1'],check=True)

def apache_restart():
	subprocess.run(['sudo', 'service','apache2','restart'],check=True)

def db_start():
	subprocess.Popen(['python3','/var/www/html/db_use.py'])

docker_start()
apache_restart()
db_start()
```

貼り付けが完了したら、`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

- メイン以外のRaspberry Piの場合

```
#メイン以外のRaspberry Pi用のコード
import subprocess

def db_start():
	subprocess.call(['python3','/home/pi/exit_entrance_app/return_nfc_reader.py'])

db_start()
```

貼り付けが完了したら、`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1. 以下のコマンドをターミナルで実行し、起動時にアプリが使えるように別のファイルを開きます。

```
sudo nano /etc/systemd/system/start_app.service
```

1. 以下のコードを貼り付けて下さい。

```
[Unit]
Description=My Docker Container and Python App
After=network.target mysql.service
[Service]
ExecStart=/usr/bin/python3 /home/pi/start_app.py
[Install]
WantedBy=multi-user.target
```

貼り付けが完了したら、`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1. 上記の手順が完了したら、以下のコマンドをターミナルで実行し設定ファイルの内容を反映させます。

```
sudo systemctl daemon-reload
```

1. 設定ファイルをRaspberry Piに登録するため、以下のコマンドをターミナルで実行します。

```
sudo systemctl enable start_app
```

1. 以下のコマンドをターミナルで実行し再起動します。

```
reboot
```

1. 再起動後は、問題なくアプリのページにつながるか・カードリーダーは動いているか・アプリ内のデータは表示されているかを確認して下さい。
2. 以下のコマンドを実行し、フォルダを移動します。

```jsx
/etc/systemd/system
```

1. 移動した先のファイルに以下のコマンドで新しいファイルを作成し、開きます。

```jsx
sudo nano start_app.timer
```

1. 開いたファイルに以下のコードをコピー・貼り付けます。

```jsx
[Unit]
Description=Restart App at 1 AM

[Timer]
OnCalendar=*-*-* 01:00:00
Persistent=true

[Install]
WantedBy=timers.target

```

貼り付けが完了したら、`Ctrl + x`を押した後に`Ctrl + y`と`Enter`で登録します。

1.  以下のコマンドをターミナルで実行して変更を反映します。

```jsx
sudo systemctl daemon-reload
sudo systemctl enable start_app.timer
sudo systemctl start start_app.timer

```

1. これにより、毎回AM1時にシステムが再起動するように設定します。

## エラー対処法・注意点

### ページを開いた際に、'AttributError'と表示される場合の対処法。

[Apacheを再起動した手順](https://www.notion.so/aed09cc0e8f04596ba16e2cb432427bc?pvs=21)の際に確認したIPアドレスを下記に当てはめ、そのURLに再アクセスして下さい。

```
'http://<IPアドレス>/sign_in'
```

### カードをかざした際、モーターが反応しないときの対処法。

ターミナルを開き、下記のコマンドを実行してフロントシステム全体を再起動します。

```
sudo systemctl restart start_app
```

それでもダメな場合は、メインRaspberry Piのターミナルにて以下のコマンドを実行し、Raspberry Pi自体を再起動してください。

```scheme
reboot
```