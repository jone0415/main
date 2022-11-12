#!/usr/local/bin/perl

# 上はサーバーにより設定変更が必要です。
# 設置に関する情報は以下のURLに解説があります。

#= ☆一言メッセージ送信CGI Ver.1.2(UTF-8版) (フリーウェア)=#
#                                                          #
# 作者HP:http://www.torawaka.jp/ToraX3/                    #
#                                                          #
#          --次の利用条件を厳守して下さい--                #
# -著作権は作者にあります。著作部分の削除、改変は禁止です。#
# -有料、無料、改造の有無に関わらず再配布は禁止致します。  #
# -本ソフトを使用したレンタル行為は禁止(有料、無料問わず)  #
# -本ソフトを使用し損害が出た場合、作者は責任を負いません  #
# -以上に同意し、自らの責任の元で利用するか判断して下さい。#
#==========================================================#

use Jcode; # (変更不要)

#==========#
# 初期設定 #
#==========#==================================================================#

$pass   = "pass_torax3";        # 管理用パスワード(必ず変更して下さい)


$confi  = 0;                    # 送信前にメッセージ内容の確認画面
                                # 0 = 確認無し / 1 = 確認画面有り

$kanryo = 0;                    # 送信完了画面のリンク指定
                                # 0 = ブラウザを閉じるリンクを付ける
                                # 1 = HPへ戻るリンクをつける

$web    = "../index.html";      # HPへ戻るアドレス(http://からもOK)

$check  = 1;                    # 日本語を含まない文字の投稿を禁止しますか？
                                # 0 = 禁止しない / 1 = 禁止する

$hostpv = 0;                    # 送信者のホスト(IP)を表示しますか？
                                # 0 = 表示しない / 1 = 表示する

#========================================#
# デザイン設定(投稿完了画面、管理画面用) #
#========================================#====================================#
$wtitle = 'メッセージ送信';     # ブラウザタイトル

$font   = "10pt";               # 基本フォントサイズ
$bgc    = "#ffffff";            # 背景色
$text   = "#000000";            # 文字色
$link   = "#8080ff";            # リンク色

#==========#
# 機能設定 #
#==========#==================================================================#
$datamax = 300;                 # 最大登録数(最大で500程度まで)
                                # あまり多くするとログ破損の恐れ有り

$dtype   = 1;                   # 上の登録数に達したら投稿を停止、又は古い記事から削除
                                # 0 = 削除 / 1 = 停止


#====================#
# 禁止ワード設定項目 #
#====================#========================================================#
# 嫌な言葉の投稿を拒否できます。

@kinsi = ('ここに禁止語を記入','ここに禁止語を記入2');

# 'と'の間の文字列の投稿を拒否
# カンマ(,)で区切れば幾つでも設定可能です。
#=============================================================================#

#================#
# メール通知設定 #
#================#============================================================#
$mailon = 0;                      # メッセージがあったらメール通知しますか？
                                  # 0 = 通知しない / 1 = 通知する

$mailad = 'none@example.com';     # する場合、メールアドレスを指定

$sendmail = '/usr/sbin/sendmail'; # sendmailのパス


#================#
# 設定はここまで #==========================#
#================# 以下、変更は自己責任で！ #================#
                 #==========================# メイン処理開始 #
                                            #================#================#

$script   = "messe.cgi";       # 本ファイル名
$datafile = "messe_log.cgi";   # データ保存ファイル

&decode;
   if($mode eq "view")   { &view;   }  # 投稿一覧
elsif($mode eq "admin")  { &admin;  }  # 管理画面入口
&html;                                 # 入口ページ

#==========#
# 作成処理 #
#==========#==================================================================#
sub html{

if(!$in{'hcom'}) { &error("コメントを入力して下さい");      }

$addr = $ENV{'REMOTE_ADDR'};
$host = gethostbyaddr(pack('C4',split(/\./,$addr)),2);

# 禁止ワードがあった場合、エラーを返す
foreach $kinsi(@kinsi){
if($in{'hcom'} =~ /$kinsi/){ 
&error("送信できませんでした。");
 }
}

# 全角文字(日本語)チェック
if($check && $in{'hcom'} !~ /(\x82[\x9F-\xF2])|(\x83[\x40-\x96])/) { &error("日本語で投稿してください。"); }

# 確認画面を表示する場合、読み込む
if($confi && !$in{'conf1'}){ &confi; }

&jikoku; # 時間を取得

# データを読込み
open(IN,"$datafile");
@lines = <IN>;
close(IN);

($bnum,$bcom,$btitle,$bhost,$bjikan) = split(/<>/, $lines[0]);

# 二重投稿を禁止する処理
if($in{'hcom'} eq "$bcom" && $in{'title'} eq "$btitle") { &error("二重送信です。<br><br>一通目を正しく送信しましたのでご安心下さい。"); }

$num = $bnum + 1;

# 最大登録数に達したら登録停止
if($dtype){
if ($datamax <= @lines)	{ &error("申し訳ございません。受付を停止しています。"); }
}else{ while ($datamax <= @lines) { pop(@lines); } }

# データを更新
unshift (@lines,"$num<>$in{'hcom'}<>$in{'title'}<>$host<>$jikan<>\n");

open(OUT,">$datafile");
print OUT @lines;
close(OUT);

if($mailon) { &mail_to; }  # メール呼び出し

&header("送信しました。");   # ヘッダー呼出し

print <<"HTML";
<center><br>
<b>以下のデータを管理人宛に送信しました</b><br>
<br>
【メッセージ】$in{'hcom'}<br><br>
HTML

# HOST表示
if($hostpv){ print "Host:$host<br>\n"; }

print <<"HTML";
<br>
ありがとうございました。
<br><br>
HTML

if($kanryo){ print "[<A href=\"$web\">戻る</A>]"; }
       else{ print "[<A href=\"javaScript:window.close()\">閉じる</A>]"; }

print "<br><br>\n";
print "</center>\n";
&footer;
exit;
}
#==========#
# 管理画面 #
#==========#==================================================================#
sub admin{
&header("管理画面");
print <<"HTML";
<center>
<br />
<b>管理画面入り口</b><br />
<br />
<form action="$script" method="POST">
<input type="hidden" name="mode" value="view">
PASS<input type="password" name="pass" size="8"><input type="submit" value="入室">
</form>
</center>
<br>
<br>
<br>
HTML
&footer;
exit;
}
#================#
# ログ一覧・削除 #
#================#============================================================#
sub view{

if($in{'pass'} ne "$pass") { &error("パスワードが違います");   }

$p_kazu = 30;   # 1ページに表示させる記事数

open(IN,"$datafile");
@lines = <IN>;
close(IN);
if ($dels[0]){
@new=();
foreach(@lines){
$flag=0;
($num,$hcom,$title,$host,$jikan) = split(/<>/, $_);
foreach $del (@dels){
if ($num eq "$del"){$flag=1; last;}
}
if($flag == 0){push(@new,$_);}
}
open(OUT,">$datafile");
print OUT @new;
close(OUT);
@lines = @new;
}
&header("データ一覧");
print <<"EOM";
<center>
<h4>データ一覧＆削除</h4>
以下がお寄せ頂いている「一言」です。<br />
削除したい場合、チェックを入れ削除ボタンを押して下さい。<br />
<BR>
[<a href="$web" target="_top">トップ</a>]<br />
<BR>
<form action="$script" method="POST">
<input type=hidden name=mode value="view">
<input type=hidden name=pass value="$in{'pass'}">
<input type=submit value="削除する">
<input type=reset value="リセット">
</CENTER>
<DL>
EOM

if($in{'start'}){
$start = $in{'start'};
if($start < 0){$start = 0;}  # $startの値が指定されていなければ0にする
}else{$start = 0;}

open(IN,"$datafile");
@lines = <IN>;
close (IN);

if($start > $#lines){$start = $#lines;}

# $startが0より大きい時「前のページ」ボタンを表示
if($start > 0){
$backflag = 1;               #「前のページ」ボタンの表示フラグ

# 前のページの先頭の件数を取得
$back = $start - $p_kazu;

# $start - $p_kazuが0より小さければ、$backを0にします
if($back < 0){$back = 0;}
}

$nextflag = 1;             # 次のページボタンの表示フラグを1にする
$next = $start + $p_kazu;  # 次のページの先頭の件数を取得
if($next > $#lines){$nextflag =0;}

if(-s $datafile){  # ログファイルチェック

for($i = $start; $i < $next; $i++){
last if($i > $#lines);    # ログの最後までを表示したら終了
$data = $lines[$i];       # $i番目のデータを得る
chop $data;
($num,$hcom,$title,$host,$jikan) = split(/<>/, $data);

print "<input type=checkbox name=del value=\"$num\">\n";
print "<B>[$jikan][$title]</B>&nbsp;$hcom&nbsp;(Host:$host)<br>\n";
print "<HR noshade size=\"1\" width=\"100%\" style=\"color:#40E0D0\">\n";
 }
}
print "</FORM><BR><BR>\n";

#「前のページ」ボタン処理  #
if($backflag){
print <<"HTML";
<center>
<table><tr><td>
<form action="$script" method="POST">
<input type="hidden" name="mode" value="view">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="start" value="$back">
<input type="submit" value="前のページ">
</form>
</td>
HTML
}
# 「次のページ」ボタン処理
if($nextflag){
if(!$backflag){
print "<center>\n";
print "<table><tr>\n";
}
print <<"HTML";
<td>
<form action="$script" method="POST">
<input type="hidden" name="mode" value="view">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="start" value="$next">
<input type="submit" value="次のページ">
</form>
</td>
HTML
}
# ボタンが表示された場合のテーブル閉じ処理
if($backflag or $nextflag) {
print "</tr></td></table>";
} # 閉じる
print "</TABLE>\n";
&footer;
exit;
}
#==========================#
# メッセージ内容の確認画面 #
#==========================#==================================================#
sub confi{

&header("メッセージの送信確認");
print <<"HTML";
<center>
<br />
<h4>メッセージの送信確認</h4>
<form action="$script" method="POST">
<input type="hidden" name="conf1" value="1">
<input type="hidden" name="title" value="$in{'title'}">
<input type="hidden" name="hcom" value="$in{'hcom'}">
以下のメッセージを送信しますがよろしいですか？<br />
<br />
<br />
$in{'hcom'}<br />
<br />
HTML

# HOST表示
if($hostpv){ print "Host:$host<br>\n"; }

print <<"HTML";
<br />
<br />
<br />
<input type="submit" value="この内容で送信する"><br />
<br />
HTML

if($kanryo){ print "[<a href=\"$web\">戻る</a>]"; }
       else{ print "[<a href=\"javaScript:window.close()\">閉じる</a>]"; }

print <<"HTML";
</form>
</center>
HTML
&footer;
exit;
}

#================#
# メール送信処理 #
#================#============================================================#
sub mail_to{

# メール本文
$mail_msg = <<"EOM";

メッセージ投稿がありました。
内容は以下のとおりです。

■投稿日時：$jikan
■ホスト名：$host
■コメント
$in{'hcom'}

------------------------

EOM

# コメント内の改行とタグを復元
$mail_msg =~ s/<br \/>/\n/ig;
$mail_msg =~ s/<br>/\n/ig;
$mail_msg =~ s/&quot;/\"/g;
$mail_msg =~ s/&lt;/</g;
$mail_msg =~ s/&gt;/>/g;

# JISコードへ変換
Jcode::convert(*mail_sub,'jis');
Jcode::convert(*mail_msg,'jis');

# メール処理
if (open(MAIL,"| $sendmail -t")) {
print MAIL "To: $mailad\n";
print MAIL "From: none\@example.com\n";
print MAIL "Subject: メッセージ投稿がありました。\n";
print MAIL "MIME-Version: 1.0\n";
print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
print MAIL "Content-Transfer-Encoding: 7bit\n";
print MAIL "X-Mailer: $ver\n\n";
print MAIL "メッセージ投稿がありました。\n";
print MAIL "--------------------------\n";
print MAIL "$mail_msg\n";
close(MAIL);
 }
}

#==============#
# デコード処理 #
#==============#==============================================================#
sub decode {
if($ENV{'REQUEST_METHOD'} eq "POST") {
read(STDIN, $formdata, $ENV{'CONTENT_LENGTH'});}
else{ $formdata = $ENV{'QUERY_STRING'}; }
@pairs = split(/&/, $formdata);
foreach $pair (@pairs) {
($name,$value) = split(/=/, $pair);
$value =~ tr/+/ /;
$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
Jcode::convert(*value,'utf8');
$value =~ s/&/&amp;/g;
$value =~ s/\"/&quot;/g;
$value =~ s/</&lt;/g;
$value =~ s/>/&gt;/g;
$value =~ s/\r\n/<br>/g;
$value =~ s/\r/<br>/g;
$value =~ s/\n/<br>/g;
if($name eq "del") { push(@dels,$value); }
$in{$name} = $value;
$mode = $in{'mode'};
 }
}
#============#
# エラー画面 #
#============#================================================================#
sub error{

&header("エラー");
print <<"HTML";
<center>
<b>エラーです。</b><br />
<br />
<font color=red>$_[0]</font><br />
<br />
<br />
HTML

if($kanryo){ print "[<a href=\"$web\">戻る</a>]<br />\n"; }
       else{ print "[<a href=\"javaScript:window.close()\">閉じる</a>]<br />\n"; }

print "<br />\n";
print "</center>\n";
&footer;
exit;
}
#==========#
# ヘッダー #
#==========#==================================================================#
sub header {
print "Content-type: text/html\n\n";
print <<"HTML";
<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>$_[0]</title></head>
<style type="text/css">
<!--
    body,th,td {font-size:$font;}
-->
</style>
<body bgcolor="$bgc" text="$text" link="$link" vlink="$link" alink="$link">
HTML
}
#==========#
# フッター #================================#
#==========# 著作権表示は削除しないで下さい #
           #================================#=================================#
sub footer{
print <<"HTML";
<center>
-<a href="http://www.torawaka.jp/ToraX3/" target="_blank">ToraX3</a>-
</center>
</body></html>
HTML
exit;
}
#======================#
# 時間取得サブルーチン #
#======================#======================================================#
sub jikoku {
$ENV{'TZ'} = "JST-9";
($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
$year=$year+1900;
$mon++;
if($mon  < 10) {$mon  = "0$mon"; }
if($mday < 10) {$mday = "0$mday";}
if($hour < 10) {$hour = "0$hour";}
if($min  < 10) {$min  = "0$min"; }
if($sec  < 10) {$sec  = "0$sec"; }
$week = ('日','月','火','水','木','金','土') [$wday];
$jikan = "$year\/$mon\/$mday($week) $hour\:$min";
}
#=============================================================================#
