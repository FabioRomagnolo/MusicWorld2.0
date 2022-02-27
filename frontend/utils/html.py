from bs4 import BeautifulSoup


def format_genius_html(html_text):
    if not html_text or html_text == '<p>?</p>':
        return None

    soup = BeautifulSoup(html_text, 'html.parser')
    a_list = soup.find_all('a')
    img_list = soup.findAll('img')
    small_list = soup.findAll('small')
    iframe_list = soup.findAll('iframe')
    for a in a_list:
        a.attrs['target'] = '_blank'
    for img in img_list:
        img.attrs['width'] = '50%'
        img.attrs['height'] = 'auto'
        img.attrs['class'] = 'center'
    for small in small_list:
        small.attrs['class'] = 'center'
    for f in iframe_list:
        f.attrs['width'] = '50%'
        f.attrs['height'] = 'auto'
        f.attrs['class'] = 'center'

    return soup.prettify()
