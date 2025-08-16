import streamlit as st #for ui
from PyPDF2 import PdfReader  #to convert pdf's text to machine readable text using the text drawing commands in the pdf
st.write("TEST")
import gensim.models as g
#this takes in the document for which we need to make embeddings and check them with the embeddings in the vector database
uploaded_file=st.file_uploader("Choose what to upload ", type="pdf") #https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader

#This is boilerplate for pypdf2 at https://pypi.org/project/PyPDF2/
if uploaded_file is not None: #if i didn't add this, it's not stopping to consider whether I've uploaded the file or not, so added. 
    reader=PdfReader(uploaded_file) #https://pypdf2.readthedocs.io/en/3.0.0/modules/PdfReader.html#PyPDF2.PdfReader
    totalpages=len(reader.pages)
    fulltext=[]
    for i in range(0,2): # further, we can increase this by replacing 2 with totalpages
        fulltext.append(reader.pages[i].extract_text())
    fulltext=" ".join(fulltext)
    st.write("Pages =",totalpages)
    st.write("Given text is : \n",fulltext)


# now we got the text, we now need to generate embeddings for all of this text

# for now, I'm using word2vec model to convert words to vector embeddings.

# read from here (https://medium.com/@manansuri/a-dummys-guide-to-word2vec-456444f3c673) that I can use word2vec from gensim.


# referenced this boilerplate from here : https://miro.medium.com/v2/resize:fit:1100/format:webp/1*Hu5A2A5Ti4pK8y5biMifEQ.png
    # in the article, they wrote (sentences=[line.split() for line in fulltext] ) but this is only because the original texts array is divided into \n separated lines. so they're splitting those again.
    fulltext=fulltext.replace("\n"," ")
    alltextaslist=fulltext.split(sep=". ") #removing all spaces, part of preprocessing.
    sentences=[]
    for line in alltextaslist:
        initial=line.split()
        sentences.append(initial)
    
    st.write("TEXT AS LIST : ",alltextaslist) 
    # now using word2vec method in gensim.models sub-section. I saw this documentation : https://radimrehurek.com/gensim/models/word2vec.html#gensim.models.word2vec.Word2Vec
    # here i had to tinker a little with the hyper parameters
    w2v=g.Word2Vec(sentences, vector_size=700, window=5, workers=4,epochs=50, min_count=2) # here size is chnged to vector_size and iter is changed to epochs as per latest api reference. I saw changes here : https://github.com/piskvorky/gensim/wiki/Migrating-from-Gensim-3.x-to-4
    words=list(w2v.wv.key_to_index)
    st.write("Vocabulary of words which come more than min_count(here, min_count=2) no. of times ",words)
    st.write("Embedding of represent : ",w2v.wv["represent"])
    st.write("Embedding of represented : ",w2v.wv["represented"])
    st.write("Similarity = ", w2v.wv.similarity('represent','represented'))

    # so now, the embeddings are coming correctly and they are giving coherent similarity scores also.

    #NOWWW, we have to store all of the embeddings of the words in the vocabulary(i.e. w2v.wv.key_to_index) in a vector database.
    # the reason for vector database would be to then make it such that this vector database stores all these embeddings with a cosine similarity such that embeddings with similar semantic/contextual meaning are grouped together.
    # then, when all of these are loaded, we then ask the user, they give the question, we convert them into embeddings, search for them in the database, return all the items with the most similarity. 
    # furthermore, we can the feed all these similar items into another llm which will convert this into human understandable sentences which will then give the correct answer.

    # i can use pgvector or milvus, since the aquilla thing is by pgvector,I'll try it.
    #But to use pgvector, I think I nee to have postgres installed in computer, but I don't have access to download.
    # the only place I know which can solve this is supabase, but donno anything related to that. Lemme see.

    # yes, saw references from https://supabase.com/docs/guides/ai/python/api and https://supabase.github.io/vecs/hosting/ and https://northflank.com/blog/postgresql-vector-search-guide-with-pgvector.

   #I tried so hard and got so far, but in the end
   # Supabase did not connect, TCP connection error at 5432 port, most probably access issues due to work laptop.
   # 
   # So, temporary soln: embeddings are stored in csv file.
    import pandas as pd
    df=pd.DataFrame(columns=['text','embedding'])
    for i in range(0,len(words)):
        df.loc[i]=[words[i],list(w2v.wv[words[i]])]
    st.dataframe(df)
    # print(list(df.loc[df['text']=='the','embedding']))

    def cosine_distance(a, b):
        return 1 - sum([a_i * b_i for a_i, b_i in zip(a, b)]) / (
        sum([a_i ** 2 for a_i in a]) ** 0.5 * sum([b_i ** 2 for b_i in b]) ** 0.5)

    #Since, database setup is done, now take input from user, make embeddings of it and compare them to these and extrat those info

    prompt=st.text_input("Ask any question relating to the document you uploaded").split()
    #If we want to give model additional context, this is where we can add, just above prompt and all combined, the embeddings will be generated
    inputtoword2vec=[]
    if prompt is not None:
        for i in prompt:
            testlist=[]
            testlist.append(i)
            inputtoword2vec.append(testlist)
        st.write("Prompt is ",prompt)
        st.write("Prompt after converting into the iterables of iterables which is the input form needed for Word2Vec is ", inputtoword2vec)
        finalembed=g.Word2Vec(inputtoword2vec, vector_size=700, window=5, workers=4,epochs=50, min_count=1)
        listofembeddings=[]
        for i in finalembed.wv.key_to_index:
            st.write(i)
            listofembeddings.append(finalembed.wv[i])
        st.write(listofembeddings)
        maximum=-2
        neededembed=[]
        for i in listofembeddings:
            for j in list(df['embedding']):
                
                tocheck=cosine_distance(i,j)
                if(tocheck>maximum):
                    maximum=tocheck
                    neededembed=j
        st.write(maximum)
        st.write(neededembed)





 