from mlc import utils
import os
import json


# GATE CSE related books: variant -> (release_tag, html_file, pdf_asset_name)
GATE_CSE_BOOKS = [
    {
        "variant": "go-cse,vol1",
        "release_tag": "gatecse-2025",
        "html_file": "book_filter1_volume1.html",
        "pdf_asset": "volume1.pdf",
        "pdf_output": "gatecse-volume1_w_cover.pdf",
    },
    {
        "variant": "go-cse,vol2",
        "release_tag": "gatecse-2025",
        "html_file": "book_filter1_volume2.html",
        "pdf_asset": "volume2.pdf",
        "pdf_output": "gatecse-volume2_w_cover.pdf",
    },
    {
        "variant": "go-cse,vol3",
        "release_tag": "gatecse-2025",
        "html_file": "book_filter1_volume3.html",
        "pdf_asset": "volume3.pdf",
        "pdf_output": "gatecse-volume3_w_cover.pdf",
    },
    {
        "variant": "go-cse,isro",
        "release_tag": "isro",
        "html_file": "book_filter2.html",
        "pdf_asset": "isro_w_cover.pdf",
        "pdf_output": "isro_w_cover.pdf",
    },
    {
        "variant": "go-cse,nielit",
        "release_tag": "NIELIT",
        "html_file": "book_filter4.html",
        "pdf_asset": "nielit_w_cover.pdf",
        "pdf_output": "nielit_w_cover.pdf",
    },
    {
        "variant": "go-cse,tifr",
        "release_tag": "tifr",
        "html_file": "book_filter5.html",
        "pdf_asset": "tifr_w_cover.pdf",
        "pdf_output": "tifr_w_cover.pdf",
    },
    {
        "variant": "go-cse,ugcnet",
        "release_tag": "ugcnet",
        "html_file": "book_filter6.html",
        "pdf_asset": "ugcnet_w_cover.pdf",
        "pdf_output": "ugcnet_w_cover.pdf",
    },
]

REPO_BASE_URL = "https://github.com/{owner}/{repo}/releases/download/{tag}/{file}"


def preprocess(i):

    env = i['env']

    repo_owner = env.get('MLC_GO_PDFS_REPO_OWNER', 'GATEOverflow')
    repo_name = env.get('MLC_GO_PDFS_REPO_NAME', 'GO-PDFs')

    # Resolve the data output path relative to script working dir or use env override
    data_output_path = env.get('MLC_GO_CSE_DATA_OUTPUT_PATH', 'data')
    if not os.path.isabs(data_output_path):
        # Make it relative to the repo root (two levels up from script dir)
        script_path = env.get('MLC_TMP_CURRENT_SCRIPT_PATH', '')
        if script_path:
            repo_root = os.path.dirname(os.path.dirname(script_path))
            data_output_path = os.path.join(repo_root, data_output_path)
        else:
            data_output_path = os.path.abspath(data_output_path)

    env['MLC_GO_CSE_DATA_PATH'] = data_output_path
    os.makedirs(data_output_path, exist_ok=True)

    # Build download commands for HTML and PDF files
    download_cmds = []
    for book in GATE_CSE_BOOKS:
        tag = book['release_tag']

        # HTML download URL
        html_url = REPO_BASE_URL.format(
            owner=repo_owner, repo=repo_name, tag=tag, file=book['html_file']
        )
        html_dest = os.path.join(data_output_path, book['html_file'])
        download_cmds.append(
            f"curl --retry 3 --retry-delay 2 -fsSL -o {html_dest!r} {html_url!r}"
        )

        # PDF download URL
        pdf_url = REPO_BASE_URL.format(
            owner=repo_owner, repo=repo_name, tag=tag, file=book['pdf_asset']
        )
        pdf_dest = os.path.join(data_output_path, book['pdf_output'])
        download_cmds.append(
            f"curl --retry 3 --retry-delay 2 -fsSL -o {pdf_dest!r} {pdf_url!r}"
        )

    env['MLC_RUN_CMD'] = " && \\\n".join(download_cmds)

    # Write metadata JSON into data folder
    metadata_path = os.path.join(data_output_path, 'gate_cse_metadata.json')
    _write_metadata(metadata_path, GATE_CSE_BOOKS, repo_owner, repo_name)

    return {'return': 0}


def postprocess(i):

    env = i['env']
    data_path = env.get('MLC_GO_CSE_DATA_PATH', 'data')
    print(f"GATE CSE data files saved to: {data_path}")

    env['MLC_DEPENDENT_CACHED_PATH'] = data_path

    return {'return': 0}


def _write_metadata(path, books, owner, repo):
    """Write gate_cse_metadata.json into the data folder."""
    metadata = {
        "description": "Metadata for GATE CSE related books generated from GATEOverflow",
        "source": "https://gateoverflow.in",
        "repository": f"https://github.com/{owner}/{repo}",
        "books": [],
    }
    for book in books:
        tag = book['release_tag']
        entry = {
            "variant": book['variant'],
            "release_tag": tag,
            "html_file": book['html_file'],
            "html_url": REPO_BASE_URL.format(
                owner=owner, repo=repo, tag=tag, file=book['html_file']
            ),
            "pdf_asset": book['pdf_asset'],
            "pdf_url": REPO_BASE_URL.format(
                owner=owner, repo=repo, tag=tag, file=book['pdf_asset']
            ),
            "pdf_output": book['pdf_output'],
        }
        metadata["books"].append(entry)

    with open(path, 'w') as f:
        json.dump(metadata, f, indent=2)
