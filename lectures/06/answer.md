# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：[search_glossary], [get_lecture_summary], [make_quiz], [search_materials]
- STEP 2 の [tool call]：glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要'}), aws_aws___search_documentation({'search_phrase': '"Using versioning" Amazon S3 overview', 'topics': ['general']})
- 気づき・疑問：第3回の際にも思ったが、ツールを使う際は最低2回モデルが呼び出され、その後tool_callのたびにモデルの呼び出し回数が増える。これは、（1）モデルが使えるツールを確認するのに1回、（2）使えるツールを再度コンテキストに投入して、最初のツールを使って1回、（3）次のツールを使って1回...（n）最後のツールを使い、コンテキストから回答を出して終了という流れになっているからなのか。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎 / 実装
- やったこと：
    - （基礎）mcpサーバーでget_lecture_summaryを公開。
    - （実装）mcpサーバーでmake_quizを公開。同様にtoolsに登録されているbrowse_treeなどの別ツールもすべて公開するコードとした。
- 結果：
    - （基礎）問題なくglossaryサーバーからget_lecture_summaryを呼び出し、第2回の内容の要約を得た。また、無事pytestも問題なく通過した。
    - （実装）こちらも問題なくmake_quizを呼び出し、第2回を指定した際は第2回の問題を出した。また、存在しない回を指定した場合は、make_quizで「第n回の用語が見つかりませんでした。」と返す設定にしていたため、第15回と指定した際は、「第15回の用語が見つからなかったため、確認問題を作成することができませんでした。」と回答が返された。
- 気づき・疑問：（基礎・実装共通）mcpサーバー経由でsearch_glossaryを呼び出す際、load_glossaryで読み込まれるglossary.jsonもmcpサーバー内に登録されるはずだが、その処理はどのように行われているのか。
