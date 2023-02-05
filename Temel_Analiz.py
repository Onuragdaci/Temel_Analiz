from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



from plotly.subplots import make_subplots 
from millify import millify
import requests
import plotly.graph_objects as go
import pandas as pd
import numpy as np 
from urllib import request
from tvDatafeed import TvDatafeed, Interval
import ssl
import streamlit as st
#python -m streamlit run app.py

Topics=[]                                                                   #Başlıklar İçin boş Liste
Tarihler=[]                                                                 #Tüm Bilanço Tarihleri
Yillar=[]                                                                   #Tüm Bİlanço Yılları
Donemler=[]                                                                 #Tüm Bilanço Tarihleri
Hisse=[]                                                                    #Analiz Edilecek Hisse Kodu
Fiyat=[]                                                                    #Analiz Edilecek Hissenin Güncel Fiyatı
Firma=[]                                                                    #Analiz Edilecek Firma Adı
X=[]


def Hisse_Temel_Veriler():
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"
    context = ssl._create_unverified_context()
    response = request.urlopen(url1, context=context)
    url1 = response.read()

    df = pd.read_html(url1,decimal=',', thousands='.')                         #Tüm Hisselerin Tablolarını Aktar
    df1=df[2]                                                                  #Tüm Hisselerin Özet Tablosu
    df2=df[6]
    df2['Sektör']=df1[['Sektör']]                                                                   
    return df2
@st.experimental_singleton
def get_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def Hisse_Piyasa_Oranlari(Hisse):
    ################################# PİYASA ORANLARI ###########################################################
    

    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    driver = get_driver()  
    driver.get("https://halkyatirim.com.tr/skorkart/"+Hisse)
    soup = BeautifulSoup(driver.page_source)
    driver.quit()
    Tum_Veri=soup.find_all("table")                                         #Tüm Veriyi Oku
    TTV = pd.read_html(str(Tum_Veri))                                       #Temel Teknik Verileri Dataframe'e dönüştür
    return TTV
def Hisse_Bilanco(Hisse):
    #İlgili Hissenin Web Sitesine Git
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse="+Hisse

    r1=requests.get(url1,verify=False)                                          #Web Sitesine Talepte Bulun
    soup=BeautifulSoup(r1.text,"html.parser")                                   #Web Sitesinin Sayfa Kaynağını Görüntüle
    FinGrp=soup.find("select",id="ddlMaliTabloGroup").find("option")["value"]   #Finansal Grubu Çek
    TarGrp=soup.find("select", id="ddlMaliTabloFirst").findChildren("option")   #Tarih Gruplarını Çek
    for j in TarGrp:
        Tarihler.append(j.string.rsplit("/"))                                    #Yilları ve Dönemleri Ayır
    for k in Tarihler:
        Yillar.append(k[0])                                                      #Yilları Tarihlerden Çek
        Donemler.append(k[1])                                                    #Dönemleri Tarihlerden Çek

    MaxRange=len(TarGrp)                                                         #Bilanço Tarihlerini Say
    if MaxRange > 12:                                                            #Bilanço Tarihleri 8 Çeyrekten Büyükse 8 Çeyreğe Eşitle
        MaxRange=12

    for i in range(MaxRange):  
        url1="https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
        
        Parametreler=(
            ("companyCode",Hisse),                                               #Hisse Kodunu Parametre Olarak Tanımla
            ("exchange","TRY"),                                                  #Türk Lirasını Parametre Olarak Tanımla
            ("financialGroup",FinGrp),                                           #Finansal Grubu Parametre Olarak Tanımla
            ("year1",Yillar[0]),                                                 #Yılları Parametre Olarak Tanımla
            ("period1",Donemler[0]),                                             #Dönemleri Parametre Olarak Tanımla
            ("year2",Yillar[1]),                                                 #Yılları Parametre Olarak Tanımla
            ("period2",Donemler[1]),                                             #Dönemleri Parametre Olarak Tanımla
            ("year3",Yillar[2]),                                                 #Yılları Parametre Olarak Tanıml
            ("period3",Donemler[2]),                                             #Dönemleri Parametre Olarak Tanımla
            ("year4",Yillar[i]),                                                 #Yılları Değişken Parametre Olarak Tanıml
            ("period4",Donemler[i]))                                             #Dönemleri Değişken Parametre Olarak Tanımla
        
        r1=requests.get(url1,params=Parametreler,verify=False).json()["value"]   #JSON formatında Sayfa Verisine Ulaş
        df2=pd.DataFrame.from_dict(r1)                                           #Sayfa Verisini Oku   
        
        if i==0:                                                                 #Sayfa İlk Kez Açılıyorsa İlk Sütün ve Son Sütunu Çek.
            df2 = df2.drop(df2.columns[[0,2,3,4,5]],axis = 1)                    #Sayfa Verisini Ayıkla    
            dfAll=[df2]                                                          #Sayfa Verisini Ana Veriye Aktar

        if i>0:                                                                  #Sayfa Tekrar Açılıyorsa Sadece Son Sütunu Çek
            df2 = df2.drop(df2.columns[[0,1,2,3,4,5]],axis = 1)                  #Sayfa Verisini Ayıkla
            dfAll.append(df2)                                                    #Sayfa Verisini Ana Veriye Aktar

    dfAll=pd.concat(dfAll,axis=1)                                                #Ana Veriyi Düzenle
    dfAll.columns.values[0] = Hisse                                              #Ana Verinin Başlıklarını Yeniden İsimlendir
    for i in range(MaxRange):                                                    #Ana Verinin Başlıkları Yeniden İsimlendir
        dfAll.columns.values[i+1] = Yillar[i] +"/"+ Donemler[i]                  #Ana Veri Başlıklarına Yılları ve DÖnemleri Yaz.

    dfAll[dfAll.columns] = dfAll.apply(lambda x: x.str.strip())                  #Ana Verideki Gereksiz Boşlukları Sil

    for col in dfAll.columns:                                                    #Ana Verideki Başlık İsimlerini Al
        X.append(col)                                                            #Başlık İsimlerini Boş Listeye Ekle
    return dfAll                                                                 #Ana Veriyi Dışarı Aktarma
def Bilanco_Analiz(dfAll,Hisse):
    ################################# BİLANÇO VERİLERİNİN ALINMASI #######################################################
    B01=dfAll[dfAll[Hisse].isin(['Dönen Varlıklar'])].reset_index(drop=True)                             #Dönen Varlıklar
    BX01=B01.drop(B01.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Dönen Varlıklar

    B02=dfAll[dfAll[Hisse].isin(['Duran Varlıklar'])].reset_index(drop=True)                             #Duran Varlıklar
    BX02=B02.drop(B02.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Duran Varlıklar

    B03=dfAll[dfAll[Hisse].isin(['Kısa Vadeli Yükümlülükler'])].reset_index(drop=True)                   #Kısa Vadeli Yükümlülükler
    BX03=B03.drop(B03.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Kısa Vadeli Yükümlülükler

    B04=dfAll[dfAll[Hisse].isin(['Uzun Vadeli Yükümlülükler'])].reset_index(drop=True)                   #Uzun Vadeli Yükümlülükler
    BX04=B04.drop(B04.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Uzun Vadeli Yükümlülükler

    B05=dfAll[dfAll[Hisse].isin(['Özkaynaklar'])].reset_index(drop=True)                                 #Özkaynaklar
    BX05=B05.drop(B05.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Özkaynaklar

    MODV=dfAll[dfAll[Hisse].isin(['Maddi Olmayan Duran Varlıklar'])].reset_index(drop=True)              #Maddi Olmayan Duran Varlıklar

    B06=dfAll[dfAll[Hisse].isin(['Ödenmiş Sermaye'])].reset_index(drop=True)                             #Ödenmiş Sermaye
    BX06=B06.drop(B06.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Ödenmiş Sermaye

    B07=dfAll[dfAll[Hisse].isin(['Dönem Net Kar/Zararı'])].reset_index(drop=True)                        #Dönem Net Kar/Zarar
    BX07=B07.drop(B07.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Dönem Net Kar/Zarar

    B08=dfAll[dfAll[Hisse].isin(['Nakit ve Nakit Benzerleri'])].reset_index(drop=True)                   #Nakit ve Nakit Benzerleri
    BX08=B08.drop(B08.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Nakit ve Nakit Benzerleri

    B09=dfAll[dfAll[Hisse].isin(['Stoklar'])].reset_index(drop=True)                                     #Stoklar

    BX09=B09.drop([1], axis=0).reset_index(drop=True)                                                    #Kısa Vadeli Stoklar
    BX09=B09.drop(B09.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Kısa Vadeli Stoklar

    B10=dfAll[dfAll[Hisse].isin(['Finansal Borçlar'])].reset_index(drop=True)                            #Finansal Borçlar

    #Finansal Borçlar
    B11=B10.drop([1], axis=0).reset_index(drop=True)                                                     #Kısa Vadeli Finansal Borçlar
    B11.at[0,Hisse]='Kısa Vadeli Finansal Borçlar'                                                       #Finansal Borcun Adını Değiştir
    BX11=B11.drop(B11.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Kısa Vadeli Finansal Borçlar

    B12=B10.drop([0], axis=0).reset_index(drop=True)                                                     #Uzun Vadeli Finansal Borçlar
    B12.at[0,Hisse]='Uzun Vadeli Finansal Borçlar'                                                       #Finansal Borcun Adını Değiştir.
    BX12=B12.drop(B12.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Uzun Vadeli Finansal Borçlar

    #Net Borç
    FY=dfAll[dfAll[Hisse].isin(['Finansal Yatırımlar'])].reset_index(drop=True)                          #Finansal Yatırımlar
    FY=FY.drop([1], axis=0).reset_index(drop=True)                                                       #Kısa Vadeli Finansal Yatırımlar
    FYX=FY.drop(FY.columns[[0]],axis = 1).to_numpy(dtype='float')                                        #Kısa Vadeli Finansal Yatırımlar

    B13=(BX11[0]+BX12[0]-FYX[0]-BX08[0]).tolist()                                                        #Kv Finansal Borçlar + Uzun Vadeli Finansal Borçlar - Nakit ve Nakit Benzerleri + Finansal Yatırımlar
    B13.insert(0,'Net Borç')                                                                             #Net Borç Adını Yaz
    B13=pd.DataFrame(B13).T                                                                              #Net Borcu DataFrame'e Çevir
    B13.set_axis(X, axis=1,inplace=True)                                                                 #Net Borç Dönemlerini Başlıklara Yaz
    BX13=B13.drop(B13.columns[[0]],axis = 1).to_numpy(dtype='float')

    B14=dfAll[dfAll[Hisse].isin(['Net YPP (Hedge Dahil)'])].reset_index(drop=True)                       #Net Yabancı Para Pozisyonu Hedge Dahil
    BX14=B14.drop(B14.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Net Yabancı Para Pozisyonu Hedge Dahil

    Bilanco= [B01,B02,B03,B04,B05,MODV,B06,B07,B08,B09,B11,B12,B13,B14]                                      #Önemli Bilanço Tablosu Verilerinin Birleştirilmesi
    Bilanco = pd.concat(Bilanco)                                                                         #Önemli Bilanço Tablosu Verilerinin Birleştirilmesi
    
    ################################# GELİR GİDER TABLOSU VERİLERİNİN ALINMASI #######################################################
    G01=dfAll[dfAll[Hisse].isin(['Satış Gelirleri'])].reset_index(drop=True)                             #Satış Gelirleri
    GX01=G01.drop(G01.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Satış Gelirleri

    G02=dfAll[dfAll[Hisse].isin(['Satışların Maliyeti (-)'])].reset_index(drop=True)                     #Satış Maliyetleri
    GX02=G02.drop(G02.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Satış Maliyetleri

    G03=dfAll[dfAll[Hisse].isin(['BRÜT KAR (ZARAR)'])].reset_index(drop=True)                            #Brüt Kar Zarar
    GX03=G03.drop(G03.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Brüt Kar Zarar

    #Pazarlama, Satış ve Dağıtım Giderleri
    G04=dfAll[dfAll[Hisse].isin(['Pazarlama, Satış ve Dağıtım Giderleri (-)'])].reset_index(drop=True)                   
    GX04=G04.drop(G04.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Pazarlama, Satış ve Dağıtım Giderleri

    G05=dfAll[dfAll[Hisse].isin(['Genel Yönetim Giderleri (-)'])].reset_index(drop=True)                 #Genel Yönetim Giderleri
    GX05=G05.drop(G05.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Genel Yönetim Giderleri

    #Araştırma ve Geliştirme Giderleri
    G06=dfAll[dfAll[Hisse].isin(['Araştırma ve Geliştirme Giderleri (-)'])].reset_index(drop=True)     
    GX06=G06.drop(G06.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Araştırma ve Geliştirme Giderleri

    G07=dfAll[dfAll[Hisse].isin(['FAALİYET KARI (ZARARI)'])].reset_index(drop=True)                      #Faaliyet Karı Zararı
    GX07=G07.drop(G07.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Faaliyet Karı Zararı

    G08=dfAll[dfAll[Hisse].isin(['Net Faaliyet Kar/Zararı'])].reset_index(drop=True)                     #Net Faaliyet Karı Zararı
    GX08=G08.drop(G08.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Net Faaliyet Karı Zararı

    G09=dfAll[dfAll[Hisse].isin(['Amortisman Giderleri'])].reset_index(drop=True)                        #Amortisman Giderleri
    GX09=G09.drop(G09.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Amortisman Gİderleri

    KT=dfAll[dfAll[Hisse].isin(['Kıdem Tazminatı'])].reset_index(drop=True)                              #Kıdem Tazminatı
    KTX=KT.drop(KT.columns[[0]],axis = 1).to_numpy(dtype='float')                                        #Kıdem Tazminatı

    G10=(GX08[0]+GX09[0]+KTX[0]).tolist()                                                                #FAVÖK = Net Faaliyet Karı/Zararı + Amortisman Giderleri + Kıdem Tazminatı
    G10.insert(0,'FAVÖK')                                                                                #FAVÖK
    G10=pd.DataFrame(G10).T                                                                              #FAVÖK'ü Dataframe'e çevir
    G10.set_axis(X, axis=1,inplace=True)                                                                 #FAVÖK Dönemlerini Başlıklara Yaz
    GX10=G10.drop(G10.columns[[0]],axis = 1).to_numpy(dtype='float')
    Gelir= [G01,G02,G03,G04,G05,G06,G07,G08,G09,G10]                                                                        #Önemli Gelir Tablosu Verilerinin Birleştirilmesi 
    Gelir = pd.concat(Gelir)                                                                                                #Önemli Gelir Tablosu Verilerinin Birleştirilmesi

    ################################# NAKİT AKIM TABLOSU VERİLERİNİN ALINMASI #######################################################
    N01=dfAll[dfAll[Hisse].isin(['İşletme Faaliyetlerinden Kaynaklanan Net Nakit'])].reset_index(drop=True)                 #İşletme Faaliyetlerinden Kaynaklanan Net Nakit
    NX01=N01.drop(N01.columns[[0]],axis = 1).to_numpy(dtype='float')                                                        #İşletme Faaliyetlerinden Kaynaklanan Net Nakit

    N02=dfAll[dfAll[Hisse].isin(['Yatırım Faaliyetlerinden Kaynaklanan Nakit'])].reset_index(drop=True)                     #Yatırım Faaliyetlerinden Kaynaklanan Nakit
    NX02=N02.drop(N02.columns[[0]],axis = 1).to_numpy(dtype='float')                                                        #Yatırım Faaliyetlerinden Kaynaklanan Nakit

    N03=dfAll[dfAll[Hisse].isin(['Finansman Faaliyetlerden Kaynaklanan Nakit'])].reset_index(drop=True)                     #Finansman Faaliyetlerinden Kaynaklanan Nakit
    NX03=N03.drop(N03.columns[[0]],axis = 1).to_numpy(dtype='float')                                                        #Finansman Faaliyetlerinden Kaynaklanan Nakit

    N04=dfAll[dfAll[Hisse].isin(['Dönem Başı Nakit Değerler'])].reset_index(drop=True)                                      #Dönem Başı Nakit Değerler
    NX04=N04.drop(N04.columns[[0]],axis = 1).to_numpy(dtype='float')                                                        #Dönem Başı Nakit Değerler

    N05=dfAll[dfAll[Hisse].isin(['Dönem Sonu Nakit'])].reset_index(drop=True)                                               #Dönem Sonu Nakit Değerler
    NX05=N05.drop(N05.columns[[0]],axis = 1).to_numpy(dtype='float')                                                        #Dönem Sonu Nakit Değerler

    N06=dfAll[dfAll[Hisse].isin(['Nakit ve Benzerlerindeki Değişim'])].reset_index(drop=True)                               #Nakit ve Nakit Benzerlerindeki Değişim
    NX06=N06.drop(N06.columns[[0]],axis = 1).to_numpy(dtype='float')                                                        #Nakit ve Nakit Benzerlerindeki Değişim

    Nakit= [N01,N02,N03,N04,N05,N06]                                                                                        #Önemli Nakit Akım Tablosu Verilerinin Birleştirilmesi  
    Nakit= pd.concat(Nakit)                                                                                                 #Önemli Nakit Akım Tablosu Verilerinin Birleştirilmesi

    ################################# LİKİDİTE ORANLARI #######################################################
    #Cari Oran
    Cari_Oran=(BX01[0]/(BX03[0]+0.001)).tolist()                                                                           #Dönen Varlıklar / Kısa Vadeli Yükümlülükler
    Cari_Oran=[round(item, 2) for item in Cari_Oran]                                                                       #Yuvarlama

    #Likidite Oranı
    Likidite_Oran=((BX01[0]-BX09[0])/(BX03[0]+0.001)).tolist()                                                             #(Dönen Varlıklar - Stoklar) / Kısa Vadeli Yükümlülükler                                                     
    Likidite_Oran=[round(item, 2) for item in Likidite_Oran]                                                               #Yuvarlama

    #Nakit Oranı
    Nakit_Oran=(BX08[0]/(BX03[0]+0.001)).tolist()                                                                          #Nakit ve Nakit Benzerleri / Kısa Vadeli Yükümlülükler
    Nakit_Oran=[round(item, 2) for item in Nakit_Oran]                                                                     #Yuvarlama
    
    LikO=pd.DataFrame(list(zip(Cari_Oran, Likidite_Oran, Nakit_Oran)),                                                     #Likidite Oranlarının Birleştirilmesi
    index=X[1:],
    columns =['Cari Oran','Likidite Oranı','Nakit Oran'])
    
    ################################# KALDIRAÇ ORANLARI #######################################################
    #Finansal Borç Oranı
    Fin_Oran=((BX11[0]+BX12[0])/(BX01[0]+BX02[0]+0.001)*100).tolist()                                                     #Toplam Finansal Borçlar / Toplam Varklıklar
    Fin_Oran=[round(item,2) for item in Fin_Oran]                                                                         #Yuvarlama

    #Kaldıraç Oranı
    Kal_Oran=((BX03[0]+BX04[0])/(BX01[0]+BX02[0]+0.001)*100).tolist()                                                     #Toplam Yükümlülükler / Toplam Varklıklar
    Kal_Oran=[round(item,2) for item in Kal_Oran]                                                                         #Yuvarlama
    
    KalO=pd.DataFrame(list(zip(Fin_Oran, Kal_Oran)),                                                                      #Kaldıraç Oranlarının Birleştirilmesi
        index=X[1:],
        columns =['Finansal Borç Oranı','Kaldıraç Oranı'])
    
    ################################# KARLILIK ORANLARI #######################################################
    #Brüt Kâr Marjı
    Brut_Marj=((GX03[0]/(GX01[0]+0.001))*100).tolist()                                                                    #Brüt Kâr / Satış Gelirleri
    Brut_Marj=[round(item,2) for item in Brut_Marj]                                                                       #Yuvarlama

    #Net Kâr Marjı
    Net_Marj=((BX07[0]/(GX01[0]+0.001))*100).tolist()                                                                     #Dönem Kârı / Satış Gelirleri
    Net_Marj=[round(item,2) for item in Net_Marj]                                                                         #Yuvarlama

    #FAVÖK Kâr Marjı
    FAVOK_Marj=((GX10[0]/(GX01[0]+0.001))*100).tolist()                                                                   #FAVÖK / Satış Gelirleri
    FAVOK_Marj=[round(item,2) for item in FAVOK_Marj]                                                                     #Yuvarlama

    #Net Borç / FAVÖK Marjı
    Net_Borc_FAVOK=(BX13[0]/(GX10[0]+0.001)).tolist()                                                                     #Net Borç / FAVÖK
    Net_Borc_FAVOK=[round(item,2) for item in Net_Borc_FAVOK]                                                             #Yuvarlama

    KarO=pd.DataFrame(list(zip(Brut_Marj, Net_Marj, FAVOK_Marj,Net_Borc_FAVOK)),                                          #Karlılık Oranlarının Birleştirilmesi
        index=X[1:],
        columns =['Brüt Kâr Marjı','Net Kâr Marjı','FAVÖK Marjı','Net Borç / FAVÖK'])

    ################################# DİĞER ORANLAR ###########################################################
    #Satış / Maliyet Marjı
    SatMal_Marj=(GX01[0]/abs(GX02[0]+0.001)).tolist()                                                                     #Satışlar/ Mutlak Satış Maaliyeti
    SatMal_Marj=[round(item,3) for item in SatMal_Marj]                                                                   #Yuvarlama

    #Pazarlama ve Satış Giderleri / Özkaynaklar
    PazGid_Marj=(abs(GX04[0])/(BX05[0]+0.001)).tolist()                                                                   #Pazarlama ve Satış Giderleri / Öz Kaynaklar
    PazGid_Marj=[round(item,3) for item in PazGid_Marj]                                                                   #Yuvarlama

    #Genel Yönetim Giderleri / Özkaynaklar
    YonGid_Marj=(abs(GX05[0])/(BX05[0]+0.001)).tolist()                                                                   #Genel Yönetim Giderleri / Öz Kaynaklar
    YonGid_Marj=[round(item,3) for item in YonGid_Marj]                                                                   #Yuvarlama

    #ARGE Giderleri / Özkaynaklar
    ARGGid_Marj=(abs(GX06[0])/(BX05[0]+0.001)).tolist()                                                                   #ARGE Giderleri / Öz Kaynaklar
    ARGGid_Marj=[round(item,2) for item in ARGGid_Marj]                                                                   #Yuvarlama

    DigO=pd.DataFrame(list(zip(SatMal_Marj, PazGid_Marj, YonGid_Marj,ARGGid_Marj)),                                       #Diğer Oranların Birleştirilmesi
        index=X[1:],
        columns =['Satış / Maaliyet','Pazarlama Giderleri / Özkaynaklar','Yönetim Giderleri / ÖzKaynaklar','ARGE/Özkaynaklar'])
    
    Oranlar=pd.concat([LikO,KalO,KarO,DigO],axis=1)                                                                       #Tüm Oranların Birleştirilmesi
    Oranlar=Oranlar.T.reset_index()                                                                                       #Oranların Transpoze Edilmesi
    Oranlar.columns.values[0] = Hisse                                                                                     #Oranlara Hisse Adı Başlığının Yazılması
    Bilanco=Bilanco.reset_index(drop=True)                                                                                #Önemli Bilanço Tablosunun Index'inin Resetlemesi
    Gelir=Gelir.reset_index(drop=True)                                                                                    #Önemli Gelir Tablosunun Index'inin Resetlenmesi
    Nakit=Nakit.reset_index(drop=True)                                                                                    #Önemli Nakit Akım Tablosunun Index'inin Resetlenmesi
    return Bilanco,Gelir,Nakit,Oranlar                                                                                    #Tüm Verilerinin Dışa Aktarılması
def Grafikler_1(df_Graph,Hisse):
    ################################# GRAFİKLER ###########################################################
    fig = make_subplots(rows=len(df_Graph.index), cols=1)
    for i in range(len(df_Graph.index)):
        FigNam=df_Graph.iloc[i].to_list()[0]
        FigDat=df_Graph.iloc[i][1:].to_numpy(dtype='float')
        FigDatText1=FigDat[::-1]
        FigDatText1=[millify(j,3) for j in FigDatText1]
        fig.add_trace(go.Scatter(name=FigNam, x=X[::-1], y=FigDat[::-1],hovertext=FigDatText1,hoverinfo='text'),row=i+1, col=1)
        fig.update_xaxes(title_text="<b>" + FigNam +"<b>", row=i+1, col=1)
        fig.update_yaxes(title_text="<b>Oran</b>",row=i+1, col=1)
    return fig
def Grafikler_2(df_Graph,Hisse):
    ################################# GRAFİKLER ###########################################################
    fig = make_subplots(rows=len(df_Graph.index), cols=1)
    for i in range(len(df_Graph.index)):
        FigNam=df_Graph.iloc[i].to_list()[0]
        FigDat=df_Graph.iloc[i][1:].to_numpy(dtype='float')
        FigDatText1=FigDat[::-1]
        FigDatText1=[millify(j,3) for j in FigDatText1]
        fig.add_trace(go.Bar(name=FigNam, x=X[::-1], y=FigDat[::-1],hovertext=FigDatText1,hoverinfo='text'),row=i+1, col=1)
        fig.update_xaxes(title_text="<b>" + FigNam +"<b>", row=i+1, col=1)
        fig.update_yaxes(title_text="<b>Türk Lirası</b>",row=i+1, col=1)
    return fig

##################################################ARAYÜZ OLUŞTURULMASI##################################################
st.set_page_config(
    page_title="Hisse Temel Analiz",
    layout="wide",
    initial_sidebar_state="expanded")

with st.sidebar:
    Hisse_Ozet=Hisse_Temel_Veriler()
    st.header('Hisse Arama')
    Hisse_Adı = st.selectbox('Hisse Adı',Hisse_Ozet['Kod'])


##################################################VERİLERİN HAZIRLANMASI##################################################
Tüm_Veri= Hisse_Bilanco(Hisse_Adı)                                                        #Bilanço Verilerilerinin Çağırılması
df_TTV = Hisse_Piyasa_Oranlari(Hisse_Adı)                                                 #Hisseye Ait Piyasa Verilerinin Çağırılması
df_Bilanco, df_Gelir, df_Nakit, df_Oranlar =Bilanco_Analiz(Tüm_Veri,Hisse_Adı)            #Bİlanço Verilerinin Ayıklanması ve Rasyoların Hesaplanması

tv = TvDatafeed()                                                                         #Data Çekmek için Trading View Uygulamasının Çağırılması
#TradingView dan Hisseye Ait Datanın Günlük Zaman Aralığında Çekilmesi
Fiyat = tv.get_hist(symbol=Hisse_Adı,exchange='BIST',interval=Interval.in_daily,n_bars=2)['close'].to_list()  
DiffPerc=100*(Fiyat[1]-Fiyat[0])/(Fiyat[0])                                               #Bir Önceki Güne Göre % Değişimin Hesaplanması
DiffPerc=round(DiffPerc,2)                                                                #Bir Önceki Güne Göre % Değişimin Yuvarlanması

Son_Durum=df_TTV[1]                                                                       #Son Durum Verilerinin Okunması
Son_Durum=Son_Durum.drop(Son_Durum.index[2:], axis=0)                                     #Son Durum Verilerinin Ayıklanması
TemV = df_TTV[4]                                                                          #Temel Verilerin Çekilmesi
TemV.columns.values[0] = Hisse_Adı                                                        #Temel Verilerin Düzenlenmesi
TemV.columns.values[1] = 'Temel Analiz Verileri'                                          #Temel Verilerin Düzenlenmesi
CarpV = df_TTV[8]                                                                         #Çarpan Verilerininin Çekilmesi
CarpV = CarpV.head(len(CarpV)-2)                                                          #Çarpan Satırlarının Azaltılması
CarpV = CarpV.drop(CarpV.columns[[2,8,9,10,11,12,13]], axis=1)                            #Çarpan Sütünlarının Azaltılması
KarV = df_TTV[7]                                                                          #Karlılık Verilerini Çek
OzserKar=KarV[KarV.columns[9]].to_list()[:12]                                             #Öz Sermaye Karlılığı
AktifKar=KarV[KarV.columns[10]].to_list()[:12]                                            #Aktif Karlılık 
OzserKar.insert(0,'Öz Sermaye Karlılığı')                                                 #Öz Sermaye Karlılığı
AktifKar.insert(0,'Aktif Karlılık')                                                       #Aktif Karlılık 
df_Oranlar.loc[len(df_Oranlar)] = AktifKar
df_Oranlar.loc[len(df_Oranlar)] = OzserKar

#Tarihsel Piyasa Çarpanları Ortalaması
CarpV['F/K'] = CarpV['F/K'].replace('-', np.nan)
CARPV_FKX=CarpV['F/K'].to_numpy(dtype='float')                                            #Tarihsel F/K Oranı                                          
CarpV['PD/DD'] = CarpV['PD/DD'].replace('-', np.nan)
CARPV_PDDDX=CarpV['PD/DD'].to_numpy(dtype='float')                                        #Tarihsel PD/DD Oranı
CarpV['FD/FAVÖK'] = CarpV['FD/FAVÖK'].replace('-', np.nan)
CARPV_FD_FAV=CarpV['FD/FAVÖK'].to_numpy(dtype='float')                                    #Tarihsel FD/FAVÖK Oranı
CarpV['FD/Satışlar'] = CarpV['FD/Satışlar'].replace('-', np.nan)
CARPV_FD_SAT=CarpV['FD/Satışlar'].to_numpy(dtype='float')                                 #Tarihsel FD/Satışlar Oranı
CARPV_FKX=np.nanmean(CARPV_FKX)                                                           #Tarihsel Ortalaması
CARPV_PDDDX=np.nanmean(CARPV_PDDDX)                                                       #Tarihsel PD/DD Ortalaması
CARPV_FD_FAV=np.nanmean(CARPV_FD_FAV)                                                     #Tarihsel FD/FAVÖK Ortalaması
CARPV_FD_SAT=np.nanmean(CARPV_FD_SAT)                                                     #Tarihsel FD/SAT Ortalaması

#BIST Piyasa Çarpanları Ortalaması 
Hisse_Ozet.replace('A/D', np.nan, inplace=True)                                           #Anlamsız Verileri NA ya çevir
BIST_FKX=Hisse_Ozet['F/K'].to_numpy(dtype='float')                                        #BIST F/K Oranı
BIST_PDDDX=Hisse_Ozet['PD/DD'].to_numpy(dtype='float')                                    #BIST PD/DD Oranı
BIST_FD_FAV=Hisse_Ozet['FD/FAVÖK'].to_numpy(dtype='float')                                #BIST FD/FAVÖK Oranı
BIST_FD_SAT=Hisse_Ozet['FD/Satışlar'].to_numpy(dtype='float')                             #BIST FD/SAT Oranı
BIST_FKX=np.nanmean(BIST_FKX)                                                             #BIST Ortalaması
BIST_PDDDX=np.nanmean(BIST_PDDDX)                                                         #BIST PD/DD Ortalaması
BIST_FD_FAV=np.nanmean(BIST_FD_FAV)                                                       #BIST FD/FAVÖK Ortalaması
BIST_FD_SAT=np.nanmean(BIST_FD_SAT)                                                       #BIST FD/SAT Ortalaması

#Sektörel Piyasa Çarpanları Ortalamalası 
Sektor=Hisse_Ozet.loc[Hisse_Ozet['Kod'] == Hisse_Adı, 'Sektör'].iloc[0]                   #Sektörün Bulunması
Filtre=Hisse_Ozet[Hisse_Ozet['Sektör'].str.contains(Sektor)]                              #Sektörel Bazlı Filtreleme
Filtre.replace('A/D', np.nan, inplace=True)                                               #Anlamsız Verileri NA ya çevir
SEKTOR_FKX=Filtre['F/K'].to_numpy(dtype='float')                                          #Sektör F/K Oranı
SEKTOR_PDDDX=Filtre['PD/DD'].to_numpy(dtype='float')                                      #Sektör PD/DD Oranı
SEKTOR_FD_FAV=Filtre['FD/FAVÖK'].to_numpy(dtype='float')                                  #Sektör FD/FAVÖK Oranı
SEKTOR_FD_SAT=Filtre['FD/Satışlar'].to_numpy(dtype='float')                               #Sektör FD/SAT Oranı
SEKTOR_FKX=np.nanmean(SEKTOR_FKX)                                                         #Sektör Ortalaması
SEKTOR_PDDDX=np.nanmean(SEKTOR_PDDDX)                                                     #Sektör PD/DD Ortalaması
SEKTOR_FD_FAV=np.nanmean(SEKTOR_FD_FAV)                                                   #Sektör FD/FAVÖK Ortalaması
SEKTOR_FD_SAT=np.nanmean(SEKTOR_FD_SAT)                                                   #Sektör FD/SAT Ortalaması

Ortalama_Basliklar=['BIST F/K','BIST PD/DD','BIST FD/FAVÖK','BIST FD/SATIŞLAR','SEKTÖR F/K','SEKTÖR PD/DD','SEKTÖR FD/FAVÖK','SEKTÖR FD/SATIŞLAR',
                'TARİHSEL F/K','TARİHSEL PD/DD','TARİHSEL FD/FAVÖK','TARİHSEL FD/SATIŞLAR']
Ortalama_Carpanlar=[BIST_FKX,BIST_PDDDX,BIST_FD_FAV,BIST_FD_SAT,SEKTOR_FKX,SEKTOR_PDDDX,SEKTOR_FD_FAV,SEKTOR_FD_SAT,CARPV_FKX,CARPV_PDDDX,CARPV_FD_FAV,CARPV_FD_SAT]
Tum_Ortalamalar=pd.DataFrame([Ortalama_Carpanlar],columns=Ortalama_Basliklar)             #Tüm Çarpan Ortalamalarının Birleştirilmesi


#Özet Bilanço Tablosunun Hazırlanması
B01=df_Bilanco[df_Bilanco[Hisse_Adı].isin(['Dönen Varlıklar'])].reset_index(drop=True)               #Dönen Varlıklar
B02=df_Bilanco[df_Bilanco[Hisse_Adı].isin(['Duran Varlıklar'])].reset_index(drop=True)               #Duran Varlıklar
B03=df_Bilanco[df_Bilanco[Hisse_Adı].isin(['Kısa Vadeli Yükümlülükler'])].reset_index(drop=True)     #Kısa Vadeli Yükümlülükler
B04=df_Bilanco[df_Bilanco[Hisse_Adı].isin(['Uzun Vadeli Yükümlülükler'])].reset_index(drop=True)     #Uzun Vadeli Yükümlülükler
B05=df_Bilanco[df_Bilanco[Hisse_Adı].isin(['Net Borç'])].reset_index(drop=True)                      #Net Borç
B06=df_Bilanco[df_Bilanco[Hisse_Adı].isin(['Özkaynaklar'])].reset_index(drop=True)                   #Özkaynaklar
B01=B01.drop(B01.columns[3::], axis=1)                                                               #Dönen Varlık Satırlarının Silinmesi
B02=B02.drop(B02.columns[3::], axis=1)                                                               #Duran Varlık Satırlarının Silinmesi
B03=B03.drop(B03.columns[3::], axis=1)                                                               #Kısa Vadeli Yükümlülükler Satırlarının Silinmesi
B04=B04.drop(B04.columns[3::], axis=1)                                                               #Uzun Vadeli Yükümlülükler Satırlarının Silinmesi
B05=B05.drop(B05.columns[3::], axis=1)                                                               #Net Borç Satırlarının Silinmesi
B06=B06.drop(B06.columns[3::], axis=1)                                                               #Özkaynaklar Satırlarının Silinmesi 

BX01=B01.drop(B01.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Dönen Varlıklar
BX01=((BX01[0][0]-BX01[0][1])/(BX01[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
BX02=B02.drop(B02.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Duran Varlıklar
BX02=((BX02[0][0]-BX02[0][1])/(BX02[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
BX03=B03.drop(B03.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Kısa Vadeli Yükümlülükler
BX03=((BX03[0][0]-BX03[0][1])/(BX03[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
BX04=B04.drop(B04.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Uzun Vadeli Yükümlülükler
BX04=((BX04[0][0]-BX04[0][1])/(BX04[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
BX05=B05.drop(B05.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Net Borç
BX05=((BX05[0][0]-BX05[0][1])/(BX05[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
BX06=B06.drop(B06.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Özkaynaklar
BX06=((BX06[0][0]-BX06[0][1])/(BX06[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
Yuzde=[BX01,BX02,BX03,BX04,BX05,BX06]                                                                #Yüzde Hesaplamalarını Birleştir
Yuzde=[round(item,2) for item in Yuzde]                                                              #Yüzde Hesaplamalarını Yuvarlama

df_Bilanco_Ozet = [B01,B02,B03,B04,B05,B06]                                                          #Özet Bilanço Verilerinin Birleştirilmesi
df_Bilanco_Ozet=pd.concat(df_Bilanco_Ozet).reset_index(drop=True)                                    #Özet Bilanço Verilerinin Birleştirilmesi
df_Bilanco_Ozet['%'] = Yuzde

#Özet Gelir Tablosunun Hazırlanması

G01=df_Gelir[df_Gelir[Hisse_Adı].isin(['Satış Gelirleri'])].reset_index(drop=True)                   #Satış Gelirleri
G02=df_Gelir[df_Gelir[Hisse_Adı].isin(['Satışların Maliyeti (-)'])].reset_index(drop=True)           #Satış Maaliyetleri
G03=df_Gelir[df_Gelir[Hisse_Adı].isin(['BRÜT KAR (ZARAR)'])].reset_index(drop=True)                  #Brüt Faaliyet Kar/Zarar
G04=df_Gelir[df_Gelir[Hisse_Adı].isin(['FAALİYET KARI (ZARARI)'])].reset_index(drop=True)            #Esas Faaliyet Kar/Zararı
G05=df_Gelir[df_Gelir[Hisse_Adı].isin(['Net Faaliyet Kar/Zararı'])].reset_index(drop=True)           #Net Faaliyet Kar/Zararı
G06=df_Gelir[df_Gelir[Hisse_Adı].isin(['FAVÖK'])].reset_index(drop=True)                             #FAVÖK
G01=G01.drop(G01.columns[6::], axis=1)                                                               #Dönen Varlık Satırlarının Silinmesi
G01=G01.drop(G01.columns[[2,3,4]], axis=1)                                                           #Dönen Varlık Satırlarının Silinmesi
G02=G02.drop(G02.columns[6::], axis=1)                                                               #Duran Varlık Satırlarının Silinmesi
G02=G02.drop(G02.columns[[2,3,4]], axis=1)                                                           #Duran Varlık Satırlarının Silinmesi
G03=G03.drop(G03.columns[6::], axis=1)                                                               #Kısa Vadeli Yükümlülükler Satırlarının Silinmesi
G03=G03.drop(G03.columns[[2,3,4]], axis=1)                                                           #Kısa Vadeli Yükümlülükler Satırlarının Silinmesi
G04=G04.drop(G04.columns[6::], axis=1)                                                               #Uzun Vadeli Yükümlülükler Satırlarının Silinmesi
G04=G04.drop(G04.columns[[2,3,4]], axis=1)                                                           #Uzun Vadeli Yükümlülükler Satırlarının Silinmesi
G05=G05.drop(G05.columns[6::], axis=1)                                                               #Net Borç Satırlarının Silinmesi
G05=G05.drop(G05.columns[[2,3,4]], axis=1)                                                           #Net Borç Satırlarının Silinmesi
G06=G06.drop(G06.columns[6::], axis=1)                                                               #Özkaynaklar Satırlarının Silinmesi 
G06=G06.drop(G06.columns[[2,3,4]], axis=1)                                                           #Özkaynaklar Satırlarının Silinmesi 

GX01=G01.drop(G01.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Dönen Varlıklar
GX01=((GX01[0][0]-GX01[0][1])/(GX01[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
GX02=G02.drop(G02.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Duran Varlıklar
GX02=((GX02[0][0]-GX02[0][1])/(GX02[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
GX03=G03.drop(G03.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Kısa Vadeli Yükümlülükler
GX03=((GX03[0][0]-GX03[0][1])/(GX03[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
GX04=G04.drop(G04.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Uzun Vadeli Yükümlülükler
GX04=((GX04[0][0]-GX04[0][1])/(GX04[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
GX05=G05.drop(G05.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Net Borç
GX05=((GX05[0][0]-GX05[0][1])/(GX05[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
GX06=G06.drop(G06.columns[[0]],axis = 1).to_numpy(dtype='float')                                     #Özkaynaklar
GX06=((GX06[0][0]-GX06[0][1])/(GX06[0][1]+0.001)*100).tolist()                                       #Yüzde Hesaplama
Yuzde=[GX01,GX02,GX03,GX04,GX05,GX06]                                                                #Yüzde Hesaplamalarını Birleştir
Yuzde=[round(item,2) for item in Yuzde]                                                              #Yüzde Hesaplamalarını Yuvarlama

df_Gelir_Ozet = [G01,G02,G03,G04,G05,G06]                                                            #Özet Gelir Tablosu Verilerinin Birleştirilmesi
df_Gelir_Ozet=pd.concat(df_Gelir_Ozet).reset_index(drop=True)                                        #Özet Gelir Tablosu Verilerinin Birleştirilmesi
df_Gelir_Ozet['%'] = Yuzde

##################################################ARAYÜZ BİLEŞENLERİ##################################################
st.title('Hisse Adı: '+ Hisse_Adı + ' Sektör: '+ Sektor)                                             #Ana Başlığın Oluşturulması
col1, col2, col3, col4, col5 ,col6 = st.columns(6)
col1.metric(label='Günlük Değişim', value=str(round(Fiyat[1],2)) + 'TL', delta=str(DiffPerc)+'%')
col2.metric('Son 1 Hafta','',Son_Durum.iat[0, 1])                                                    #Haftalık Değişimin Gösterilmesi
col3.metric('Son 1 Ay','',Son_Durum.iat[0, 2])                                                       #Aylık Değişimin Gösterilmesi
col4.metric('Son 3 Ay','',Son_Durum.iat[0, 3])                                                       #3 Aylık Değişimin Gösterilmesi
col5.metric('Son 6 Ay','',Son_Durum.iat[0, 4])                                                       #6 Aylık Değişimin Gösterilmesi
col6.metric('Son 1 Yıl','',Son_Durum.iat[0, 5])                                                      #Yıllık Değişimin Gösterilmesi

col1, col2 =st.columns(2)
col1.subheader('Özet Gelir Tablosu')
col1.dataframe(df_Gelir_Ozet,use_container_width=True)
col2.subheader('Özet Bilanço Tablosu')
col2.dataframe(df_Bilanco_Ozet,use_container_width=True)

col1, col2 =st.columns(2)
col1.subheader('Güncel Piyasa Çarpanları')

col1.dataframe(TemV,use_container_width=True)
col2.subheader('Tarihsel Piyasa Çarpanları')
col2.dataframe(CarpV,use_container_width=True)

st.subheader('BIST ,Sektörel ve Tarihsel Piyasa Çarpanları')
st.dataframe(Tum_Ortalamalar,use_container_width=True)

st.subheader('Veriler')
with st.expander('Rasyolar',expanded=False):
    st.dataframe(df_Oranlar,use_container_width=True)

with st.expander('Tüm Bilanço Kalemleri',expanded=False):
    st.dataframe(Tüm_Veri,use_container_width=True)

with st.expander('Önemli Bilanço Kalemleri',expanded=False):
    st.dataframe(df_Bilanco, use_container_width=True)

with st.expander('Önemli Gelir-Gider Tablosu Kalemleri',expanded=False):
    st.dataframe(df_Gelir,use_container_width=True)

with st.expander('Önemli Nakit Akım Tablosu Kalemleri',expanded=False):
    st.dataframe(df_Nakit,use_container_width=True)

st.subheader('Grafikler')
with st.expander('Rosyo Grafikleri'):
    with st.container():
        fig1=Grafikler_1(df_Oranlar,Hisse_Adı)
        fig1.update_layout(showlegend = False, height=4000)
        st.plotly_chart(fig1,use_container_width=True)

with st.expander('Tarihsel Piyasa Çarpanları Grafikleri'):
    with st.container():
        CarpV = CarpV.T.reset_index() 
        CarpV=CarpV.drop(CarpV.columns[12:], axis=1)
        CarpV=CarpV.iloc[1: , :]
        fig2=Grafikler_1(CarpV,Hisse_Adı)
        fig2.update_layout(showlegend = False, height=4000)
        st.plotly_chart(fig2,use_container_width=True)

with st.expander('Önemli Bilanço Tablosu Grafikleri'):
    with st.container():
        fig3=Grafikler_2(df_Bilanco,Hisse_Adı)
        fig3.update_layout(showlegend = False, height=4000)
        st.plotly_chart(fig3,use_container_width=True)

with st.expander('Önemli Gelir-Gider Tablosu Grafikleri'):
    with st.container():
        fig4=Grafikler_2(df_Gelir,Hisse_Adı)
        fig4.update_layout(showlegend = False, height=4000,width=1600)
        st.plotly_chart(fig4,use_container_width=True)

with st.expander('Önemli Nakit Akım Tablosu Grafkleri'):
    with st.container():
        fig5=Grafikler_2(df_Nakit,Hisse_Adı)
        fig5.update_layout(showlegend = False, height=4000,width=1600)
        st.plotly_chart(fig5,use_container_width=True)

with st.expander('Tüm Bilanço Tablosu Grafikleri'):
    with st.container():
        fig5=Grafikler_2(Tüm_Veri,Hisse_Adı)
        fig5.update_layout(showlegend = False, height=50000,width=1600)
        st.plotly_chart(fig5,use_container_width=True)
