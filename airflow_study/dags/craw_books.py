import requests
from bs4 import BeautifulSoup
import pandas as pd
from airflow.models import XCom
from io import StringIO
from urllib import robotparser

__all__ = ['get_books']

def check_robotstxt(url):
    # 웹사이트의 robots.txt 파일을 확인하는 함수
    base_url = '/'.join(url.split('/')[:3])
    robots_url = f"{base_url}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch("*", url)

def get_books(**kwargs):
    daily_top200_book_list = []
    rank = 1
    
    # 크롤링할 사이트 URL
    url = 'https://www.yes24.com/Product/Category/BestSeller?categoryNumber=001&pageNumber={page}&pageSize=24'

    # robots.txt를 확인하고 크롤링이 허용되는지 확인
    if not check_robotstxt(url):
        print("로봇.txt에 의해 크롤링이 허용되지 않습니다.")
        return

    for page in range(1, 11):
        full_url = url.format(page=page)
        response = requests.get(full_url)
        
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # 책 목록을 포함하는 최상위 li 태그 선택
            book_list = soup.select('li[data-goods-no]')
            
            for book in book_list:
                # 책 제목 추출
                title = book.select_one('.item_info .info_row.info_name .gd_name').text.strip()

                # 저자 정보 추출
                author = book.select_one('.info_row.info_pubGrp .authPub.info_auth').text.replace('저', '').strip()
                
                # 출판사 정보 추출
                publish_company = book.select_one('.info_row.info_pubGrp .authPub.info_pub').text.strip()

                # 출판 날짜 정보 추출
                publish_date = book.select_one('.info_row.info_pubGrp .authPub.info_date').text.strip()

                # 가격 정보 추출
                price = book.select_one('.info_row.info_price .yes_b').text.strip().replace('원', '').replace(',', '')

                # 리뷰 수 추출 (리뷰가 없는 경우 '0'으로 설정)
                review_count = book.select_one('.rating_rvCount .txC_blue')
                review_count = review_count.text.strip() if review_count else '0'

                # 책 상세 페이지 링크 추출
                link = book.select_one('.item_info .info_row.info_name a')
                link = 'https://www.yes24.com' + link['href'] if link else None

                # 리스트에 추가
                daily_top200_book_list.append([
                    rank, title, author, price, publish_company, 
                    publish_date, review_count, link
                ])
                rank += 1
        else:
            print(f"Error fetching page {page}, status code: {response.status_code}")
    
    # 데이터프레임 생성
    data = pd.DataFrame(daily_top200_book_list, columns=[
        'rank', 'title', 'author', 'price', 'publishing_house',
        'publication_date', 'review_count', 'link'
    ])
    
    # 데이터프레임을 CSV 문자열로 변환
    csv_data = data.to_csv(index=False)
    print("★★★★★★★★★★★★data★★★★★★★★★★★:", data)
    print("csv_data:", csv_data)

    # XCom으로 CSV 문자열 전달
    kwargs['ti'].xcom_push(key='data', value=csv_data)
