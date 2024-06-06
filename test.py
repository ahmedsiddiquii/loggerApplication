import httpx


def upload_pdf_report_exec(path, usb_label):
    response = httpx.post(
        'https://equartz.tech/pdf/upload_pdf.php',
        data={'serial_no': usb_label},
        files={'pdf_file': open(path, 'rb')},
        headers={'User-Agent': 'PostmanRuntime/7.29.10'},
    )

    if response.status_code == 200:
        print('Successfully uploaded the PDF file!')
    else:
        print(f"PDF file upload failed {response.text}")
upload_pdf_report_exec(r"C:\Users\Carlo\PycharmProjects\loggerApplication\REPORT.PDF","TEST")