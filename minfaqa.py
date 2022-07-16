import json

from flask import Flask, request
from py2neo import Graph
from pyhanlp import *

app = Flask(__name__)


@app.route("/qa", methods=['POST', 'GET'])
def kg_qa():
    if request.method == 'GET':

        ques = request.args.get('question')
        cb = request.args.get('callback')
        print(ques)

        qa_graph = Graph('http://localhost:7474', username='neo4j', password='123456')
        keyword = []
        ansList = []
        # CRF 词法分析器
        CRFLexicalAnalyzer = JClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")
        analyzer = CRFLexicalAnalyzer()
        han_word_pos = analyzer.analyze(ques).toString()

        print(han_word_pos)

        wordlist = han_word_pos.split(" ")
        for word in wordlist:
            pos = word.split("/")
            if "n" in pos[1] or "v" in pos[1] or "a" in pos[1]:
                #print(pos[0], pos[1])
                if pos[0] not in keyword:
                    keyword.append(pos[0])
        print(keyword)
        query_str = ""
        # 枚举组成cypher查询语句
        for key1 in keyword:
            for key2 in keyword:
                query_str = "match (e)-[r:`属于`]->(s) where  e.name=~'.*%s.*' return e.name" % (key1)
                #query_str = "match (e)-[r:`属于`]->(s) where e.name='%s' return s.name" % (key1)

                if (len(query_str) > 0):
                    answer = qa_graph.run(query_str).data()

                    if answer:
                        for item in answer:
                            #print(item)
                            ans_str = item['e.name']
                            #print(ans_str)
                            # 如果结果里面没有才加入
                            if ans_str not in ansList:
                                ansList.append(ans_str)
            print(query_str)
            print(answer)
        print(ansList)

        re_ans = "该案例可能属于：\n"

        for i in range(len(ansList)):
            re_ans += "(%s) %s \n" % (i + 1, ansList[i])
        print(re_ans)

        result = {
            "question": ques,
            "answer": re_ans
        }
        res_str = json.dumps(result)
        cb_str = cb + "(" + res_str + ")"
        print(cb_str)

        return cb_str
    return 'Error Format'


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    run_simple('127.0.0.1', 9001, app)
