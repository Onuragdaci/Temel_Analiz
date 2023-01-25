from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

    df1 = pd.read_html(url1,decimal=',', thousands='.')                         #Tüm Hisselerin Tablolarını Aktar
    df1=df1[2]                                                                  #Tüm Hisselerin Özet Tablosu
    return df1
def Hisse_Piyasa_Oranlari(Hisse):
    ################################# PİYASA ORANLARI ###########################################################
    options = Options()
    options.headless = True
    driver = webdriver.Chrome (executable_path="C:\\chromedriver.exe", options=options)    
    driver.get("https://halkyatirim.com.tr/skorkart/"+Hisse)
    soup = BeautifulSoup(driver.page_source)
    Tum_Veri=soup.find_all("table")                                         #Tüm Veriyi Oku
    TemV = pd.read_html(str(Tum_Veri))[4]                                   #Tüm Veriyi Dataframe'e dönüştür

    FinV = pd.read_html(str(Tum_Veri))[6]                                   #Finansal Verileri Çek
    FinV = FinV.drop(FinV.index[12:], axis=0)                               #Finansal Satırları Azalt
    FinV = FinV.drop(FinV.columns[[1,3,5,6,7,9,10,11,12,13]], axis=1)         #Finansal Sütünları Azalt
    KarV = pd.read_html(str(Tum_Veri))[7]                                   #Karlılık Verilerini Çek
    KarV = KarV.drop(KarV.index[12:], axis=0)                               #Karlılık Satırları Azalt

    CarpV = pd.read_html(str(Tum_Veri))[8]                                  #Çarpan Verilerini Çek
    CarpV = CarpV.drop(CarpV.index[12:], axis=0)                            #Çarpan Satırları Azalt
    CarpV = CarpV.drop(CarpV.columns[[1,2,8,9,10]], axis=1)                #Çarpan Sütünları Azalt

    driver.quit()
    return TemV,FinV, KarV, CarpV
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
    return dfAll
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

    Bilanco= [B01,B02,B03,B04,B05,B06,B07,B08,B11,B12,B13,B14]                                           # Bilanço Verilerini Birleştir.
    Bilanco = pd.concat(Bilanco)
    
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
    Gelir= [G01,G02,G03,G04,G05,G06,G07,G08,G09,G10]  
    Gelir = pd.concat(Gelir)

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

    Nakit= [N01,N02,N03,N04,N05,N06]  
    Nakit= pd.concat(Nakit)

    ################################# LİKİDİTE ORANLARI #######################################################
    #Cari Oran
    Cari_Oran=(BX01[0]/(BX03[0]+0.001)).tolist()                                                                           #Dönen Varlıklar / Kısa Vadeli Yükümlülükler
    Cari_Oran=[round(item, 2) for item in Cari_Oran]

    #Likidite Oranı                                                                                                        #(Dönen Varlıklar - Stoklar) / Kısa Vadeli Yükümlülükler
    Likidite_Oran=((BX01[0]-BX09[0])/(BX03[0]+0.001)).tolist()                                                     
    Likidite_Oran=[round(item, 2) for item in Likidite_Oran]

    #Nakit Oranı                                                                                                           #Nakit ve Nakit Benzerleri / Kısa Vadeli Yükümlülükler
    Nakit_Oran=(BX08[0]/(BX03[0]+0.001)).tolist()
    Nakit_Oran=[round(item, 2) for item in Nakit_Oran]
    
    LikO=pd.DataFrame(list(zip(Cari_Oran, Likidite_Oran, Nakit_Oran)), 
    index=X[1:],
    columns =['Cari Oran','Likidite Oranı','Nakit Oran'])
    ################################# KALDIRAÇ ORANLARI #######################################################
    #Finansal Borç Oranı                                                                                                   #Toplam Finansal Borçlar / Toplam Varklıklar
    Fin_Oran=((BX11[0]+BX12[0])/(BX01[0]+BX02[0]+0.001)*100).tolist()
    Fin_Oran=[round(item,2) for item in Fin_Oran]

    #Kaldıraç Oranı                                                                                                        #Toplam Yükümlülükler / Toplam Varklıklar
    Kal_Oran=((BX03[0]+BX04[0])/(BX01[0]+BX02[0]+0.001)*100).tolist()
    Kal_Oran=[round(item,2) for item in Kal_Oran]
    
    KalO=pd.DataFrame(list(zip(Fin_Oran, Kal_Oran)),
        index=X[1:],
        columns =['Finansal Borç Oranı','Kaldıraç Oranı'])
    ################################# KARLILIK ORANLARI #######################################################
    #Brüt Kâr Marjı                                                                                                        #Brüt Kâr / Satış Gelirleri
    Brut_Marj=((GX03[0]/(GX01[0]+0.001))*100).tolist()
    Brut_Marj=[round(item,2) for item in Brut_Marj]

    #Net Kâr Marjı                                                                                                         #Dönem Kârı / Satış Gelirleri
    Net_Marj=((BX07[0]/(GX01[0]+0.001))*100).tolist()
    Net_Marj=[round(item,2) for item in Net_Marj]

    #FAVÖK Kâr Marjı                                                                                                       #FAVÖK / Satış Gelirleri
    FAVOK_Marj=((GX10[0]/(GX01[0]+0.001))*100).tolist()
    FAVOK_Marj=[round(item,2) for item in FAVOK_Marj]

    #Net Borç / FAVÖK Marjı                                                                                                 #Net Borç / FAVÖK
    Net_Borc_FAVOK=(BX13[0]/(GX10[0]+0.001)).tolist()
    Net_Borc_FAVOK=[round(item,2) for item in Net_Borc_FAVOK]

    KarO=pd.DataFrame(list(zip(Brut_Marj, Net_Marj, FAVOK_Marj,Net_Borc_FAVOK)),
        index=X[1:],
        columns =['Brüt Kâr Marjı','Net Kâr Marjı','FAVÖK Marjı','Net Borç / FAVÖK'])

    ################################# DİĞER ORANLAR ###########################################################
    #Satış / Maliyet Marjı                                                                                                 #Satışlar/ Mutlak Satış Maaliyeti
    SatMal_Marj=(GX01[0]/abs(GX02[0]+0.001)).tolist()
    SatMal_Marj=[round(item,3) for item in SatMal_Marj]

    #Pazarlama ve Satış Giderleri / Özkaynaklar                                                                            #Pazarlama ve Satış Giderleri / Öz Kaynaklar
    PazGid_Marj=(abs(GX04[0])/(BX05[0]+0.001)).tolist()
    PazGid_Marj=[round(item,3) for item in PazGid_Marj]

    #Genel Yönetim Giderleri / Özkaynaklar                                                                                 #Genel Yönetim Giderleri / Öz Kaynaklar
    YonGid_Marj=(abs(GX05[0])/(BX05[0]+0.001)).tolist()
    YonGid_Marj=[round(item,3) for item in YonGid_Marj]

    #ARGE Giderleri / Özkaynaklar                                                                                          #ARGE Giderleri / Öz Kaynaklar
    ARGGid_Marj=(abs(GX06[0])/(BX05[0]+0.001)).tolist()
    ARGGid_Marj=[round(item,2) for item in ARGGid_Marj]

    DigO=pd.DataFrame(list(zip(SatMal_Marj, PazGid_Marj, YonGid_Marj,ARGGid_Marj)),
        index=X[1:],
        columns =['Satış / Maaliyet','Pazarlama Giderleri / Özkaynaklar','Yönetim Giderleri / ÖzKaynaklar','ARGE/Özkaynaklar'])
    Oranlar=pd.concat([LikO,KalO,KarO,DigO],axis=1)
    return Bilanco,Gelir,Nakit,Oranlar
def Hisse_Grafikler(Hisse):
    ################################# GRAFİKLER ###########################################################
    fig1 = make_subplots(rows=len(df_Bilanco.index), cols=2)
    fig2 = make_subplots(rows=len(df_Gelir.index), cols=2)
    fig3 = make_subplots(rows=len(df_Nakit.index), cols=2)

    for i in range(len(df_Bilanco.index)):
        FigNam=df_Bilanco.iloc[i].to_list()[0]
        FigDat=df_Bilanco.iloc[i][1:].to_numpy(dtype='float')
        FDPercVal = FigDat[::-1]
        FigDatPerc=[1]    
        for j in range(len(FigDat)-1):
            if FigDat[j]==0:
                FigDatPerc.append(0)
            if FigDat[j+1]!=0:
                FigDatPerc.append(FDPercVal[j+1]/(FDPercVal[j]+0.001))
        
        FigDatText1=FigDat[::-1]
        FigDatText2=FigDatPerc
    
        FigDatText1=[millify(j,3) for j in FigDatText1]

        fig1.add_trace(go.Bar(name=FigNam, x=X[::-1], y=FigDat[::-1],hovertext=FigDatText1,hoverinfo='text'),row=i+1, col=1)
        fig1.add_trace(go.Scatter(name=FigNam, x=X[::-1], y=FigDatPerc,hovertext=FigDatText2,hoverinfo='text'),row=i+1, col=2)
        
        fig1.update_xaxes(title_text="<b>" + Hisse + " " + FigNam +"<b>", row=i+1, col=1)
        fig1.update_xaxes(title_text="<b>" + Hisse + " " + FigNam +"<b>", row=i+1, col=2)
        fig1.update_yaxes(title_text="<b>Türk Lirası</b>",row=i+1, col=1)
        fig1.update_yaxes(title_text="<b>Oran Türk Lirası</b>",row=i+1, col=2)

    for i in range(len(df_Gelir.index)):
        FigNam=df_Gelir.iloc[i].to_list()[0]
        FigDat=df_Gelir.iloc[i][1:].to_numpy(dtype='float')
        FDPercVal = FigDat[::-1]
        FigDatPerc=[1]    
        for j in range(len(FigDat)-1):
            if FigDat[j]==0:
                FigDatPerc.append(0)
            if FigDat[j+1]!=0:
                FigDatPerc.append(FDPercVal[j+1]/(FDPercVal[j]+0.001))
        
        FigDatText1=FigDat[::-1]
        FigDatText1=[millify(j,3) for j in FigDatText1] 
        
        FigDatText2=FigDatPerc
        fig2.add_trace(go.Bar(name=FigNam, x=X[::-1], y=FigDat[::-1],hovertext=FigDatText1,hoverinfo='text'),row=i+1, col=1)
        fig2.add_trace(go.Scatter(name=FigNam, x=X[::-1], y=FigDatPerc,hovertext=FigDatText2,hoverinfo='text'),row=i+1, col=2)
        
        fig2.update_xaxes(title_text="<b>" + Hisse + " " + FigNam +"<b>", row=i+1, col=1)
        fig2.update_xaxes(title_text="<b>" + Hisse + " " + FigNam +"<b>", row=i+1, col=2)
        fig2.update_yaxes(title_text="<b>Türk Lirası</b>",row=i+1, col=1)
        fig2.update_yaxes(title_text="<b>Oran Türk Lirası</b>",row=i+1, col=2)

    for i in range(len(df_Nakit.index)):
        FigNam=df_Nakit.iloc[i].to_list()[0]
        FigDat=df_Nakit.iloc[i][1:].to_numpy(dtype='float')
        FDPercVal = FigDat[::-1]
        FigDatPerc=[1]    
        for j in range(len(FigDat)-1):
            if FigDat[j]==0:
                FigDatPerc.append(0)
            if FigDat[j+1]!=0:
                FigDatPerc.append(FDPercVal[j+1]/(FDPercVal[j]+0.001))
        
        FigDatText1=FigDat[::-1]
        FigDatText1=[millify(j,3) for j in FigDatText1] 
        FigDatText2=FigDatPerc
        FigDatText2=[round(item, 2) for item in FigDatText2]

        fig3.add_trace(go.Bar(name=FigNam, x=X[::-1], y=FigDat[::-1],hovertext=FigDatText1,hoverinfo='text'),row=i+1, col=1)
        fig3.add_trace(go.Scatter(name=FigNam, x=X[::-1], y=FigDatPerc,hovertext=FigDatText2,hoverinfo='text'),row=i+1, col=2)
        
        fig3.update_xaxes(title_text="<b>" + Hisse + " " + FigNam +"<b>", row=i+1, col=1)
        fig3.update_xaxes(title_text="<b>" + Hisse + " " + FigNam +"<b>", row=i+1, col=2)
        fig3.update_yaxes(title_text="<b>Türk Lirası</b>",row=i+1, col=1)
        fig3.update_yaxes(title_text="<b>Oran Türk Lirası</b>",row=i+1, col=2)

    fig1.update_layout(showlegend = False)
    fig1.update_layout(height=4000, width=1600, title_text="<b>Hisse Kodu: </b>" + Hisse +"<b> Hisse Adı: </b>"+ Hisse+"<b> Bilanço Tablosu</b>")

    fig2.update_layout(showlegend = False)
    fig2.update_layout(height=4000, width=1600, title_text="<b>Hisse Kodu: </b>" + Hisse +"<b> Hisse Adı: </b>"+ Hisse+"<b> Gelir Tablosu</b>")

    fig3.update_layout(showlegend = False)
    fig3.update_layout(height=4000, width=1600, title_text="<b>Hisse Kodu: </b>" + Hisse +"<b> Hisse Adı: </b>"+ Hisse+"<b> Nakit Akım Tablosu</b>")

    fig1.write_html("C:/Users/onura/Desktop/Borsa/"+Hisse+"Bilanco.html")
    fig2.write_html("C:/Users/onura/Desktop/Borsa/"+Hisse+"Gelir_Tablosu.html")
    fig2.write_html("C:/Users/onura/Desktop/Borsa/"+Hisse+"Nakit_Tablosu.html")
    fig1.show()
    fig2.show()
    fig3.show()

st.set_page_config(
    page_title="Hisse Temel Analiz",
    layout="wide",
    initial_sidebar_state="expanded")

with st.sidebar:
    Hisse_Temel=Hisse_Temel_Veriler()
    st.header('Hisse Arama')
    Sektor=Hisse_Temel['Sektör'].drop_duplicates()                              #Sektörleri Filtrele
    dropdown1 = st.selectbox('Sektör',Sektor)
    Hisse_Kodlari=Hisse_Temel[Hisse_Temel['Sektör'].str.contains(dropdown1)]
    dropdown2 = st.selectbox('Hisse Adı',Hisse_Kodlari['Kod'])
    Tüm_Veri= Hisse_Bilanco(dropdown2)
    #dropdown3 = st.selectbox('Bilanço Kalemi',Tüm_Veri[dropdown2])
    #print(Tüm_Veri[dropdown2])
Temel_Veriler,Finansallar, Karlilik, Carpanlar = Hisse_Piyasa_Oranlari(dropdown2)
df_Bilanco, df_Gelir, df_Nakit, df_Oranlar =Bilanco_Analiz(Tüm_Veri,dropdown2)
st.write(df_Bilanco)
st.write(df_Gelir)
st.write(df_Nakit)
st.write(df_Oranlar)
st.write(Temel_Veriler)
st.write(Finansallar)
st.write(Karlilik)
st.write(Carpanlar)
#Hisse_Grafikler(Hisse[0])
