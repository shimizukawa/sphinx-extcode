sphinx-extcode - Sphinx extension
==================================

:repository: https://github.com/shimizukawa/sphinx-extcode
:documentation: https://shimizukawa.github.io/sphinx-extcode/
:license: MIT License

目的
====

1つの ``code-block`` ディレクティブでサンプルのreSTソースを書くだけで、ソースとそのレンダリング結果の両方を表示します。


設定
====

.. code-block:: python

   extensions = [
       'extcode',
   ]

   extcode = {
       #'rendered-block': 'vertical',  デフォルトの動作を設定したい場合
   }



利用例
======

コードブロックを以下のように書きます

.. code-block:: rst

   .. code-block:: rst
      :rendered-block: vertical

      単語を * で囲うと *強調* になります。

      ** は **より強い強調** に使います。

      `` （バッククオート） は ``make html`` のようにコードなどを表現します。

      `Sphinx-users.jp <http://sphinx-users.jp/>`_ はSphinxの情報を発信しています。

      リンクは `このように書いて`_ 、以降の行でURLを設定することもできます。

      .. _このように書いて: http://sphinx-doc.org/

``:rendered-block: vertical`` のように、オプションを指定できるように ``code-block`` ディレクティブを拡張しています。
オプションには ``vertical``, ``horizontal``, ``toggle``, ``tab`` を指定できます。

vertical - 縦に並べる
---------------------

.. code-block:: rst
   :rendered-block: vertical

   単語を * で囲うと *強調* になります。

   ** は **より強い強調** に使います。

   `` （バッククオート） は ``make html`` のようにコードなどを表現します。

   `Sphinx-users.jp <http://sphinx-users.jp/>`_ はSphinxの情報を発信しています。

   リンクは `このように書いて`_ 、以降の行でURLを設定することもできます。

   .. _このように書いて: http://sphinx-doc.org/


horizontal - 横に並べる
------------------------

.. code-block:: rst
   :rendered-block: horizontal

   単語を * で囲うと *強調* になります。

   ** は **より強い強調** に使います。

   `` （バッククオート） は ``make html`` のようにコードなどを表現します。

   `Sphinx-users.jp <http://sphinx-users.jp/>`_ はSphinxの情報を発信しています。

   リンクは `このように書いて`_ 、以降の行でURLを設定することもできます。

   .. _このように書いて: http://sphinx-doc.org/


toggle - 右上のマークで切り替え
--------------------------------

.. code-block:: rst
   :rendered-block: toggle

   単語を * で囲うと *強調* になります。

   ** は **より強い強調** に使います。

   `` （バッククオート） は ``make html`` のようにコードなどを表現します。

   `Sphinx-users.jp <http://sphinx-users.jp/>`_ はSphinxの情報を発信しています。

   リンクは `このように書いて`_ 、以降の行でURLを設定することもできます。

   .. _このように書いて: http://sphinx-doc.org/


tab - タブで切り替え
--------------------

tabは未実装です

