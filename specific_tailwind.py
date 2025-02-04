from bs4 import BeautifulSoup

def style_html_with_tailwind(html_content):
    # Parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Style <p> tags
    for p in soup.find_all('p'):
        if 'ql-align-justify' in p.get('class', []):
            p['class'] = p.get('class', []) + ['text-justify', 'mt-4', 'text-gray-700']
        elif 'ql-align-center' in p.get('class', []):
            p['class'] = p.get('class', []) + ['text-center', 'mt-4', 'text-gray-700']
        elif 'ql-indent-1' in p.get('class', []):
            p['class'] = p.get('class', []) + ['ml-1', 'text-gray-700']
        elif 'ql-indent-2' in p.get('class', []):
            p['class'] = p.get('class', []) + ['ml-2', 'text-gray-700']
        elif 'ql-indent-3' in p.get('class', []):
            p['class'] = p.get('class', []) + ['ml-3', 'text-gray-700']
        elif 'ql-indent-4' in p.get('class', []):
            p['class'] = p.get('class', []) + ['ml-4', 'text-gray-700']
        else:
            p['class'] = p.get('class', []) + ['mt-4', 'text-gray-700']

    for tag in soup.find_all('div'):
        if tag.find('h2') or tag.find('ul'):  # Check if the div contains these tags
            tag['class'] = tag.get('class', []) + ['mt-8']
            
    # Style <h1> tags
    for h1 in soup.find_all('h1'):
        h1['class'] = h1.get('class', []) + ['text-2xl', 'font-semibold', 'mt-4', 'mb-6', 'text-gray-800']

    for tag in soup.find_all('h2'):
        tag['class'] = tag.get('class', []) + ['text-xl', 'font-semibold', 'mb-4', 'mt-6']
        
    # Style <ul> and <ol> tags
    for ul in soup.find_all('ul'):
        ul['class'] = ul.get('class', []) + ['list-disc', 'list-inside', 'text-gray-700', 'leading-relaxed', 'space-y-2', 'ml-2']
    for ol in soup.find_all('ol'):
        ol['class'] = ol.get('class', []) + ['list-decimal', 'list-inside', 'text-gray-700', 'leading-relaxed', 'space-y-2', 'ml-2']

    # Style <li> tags
    for li in soup.find_all('li'):
        li['class'] = li.get('class', []) + ['mt-1']

    # Style <a> tags
    for a in soup.find_all('a'):
        a['class'] = a.get('class', []) + ['text-blue-600', 'hover:underline', 'font-bold']

    # Style <blockquote> tags
    for blockquote in soup.find_all('blockquote'):
        blockquote['class'] = blockquote.get('class', []) + ['border-l-4', 'border-gray-300', 'pl-4', 'italic', 'text-gray-600', 'mt-4']

    # Style <strong>, <em>, and <u> tags if needed
    for strong in soup.find_all('strong'):
        strong['class'] = strong.get('class', []) + ['font-semibold']
    for em in soup.find_all('em'):
        em['class'] = em.get('class', []) + ['italic']
    for u in soup.find_all('u'):
        u['class'] = u.get('class', []) + ['underline']

    # Return the styled HTML
    return str(soup)
