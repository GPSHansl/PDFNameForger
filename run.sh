#!/bin/bash
# Helper script to work with the PDF Renamer in Docker

set -e

function show_help() {
    echo "PDF Renamer Docker Helper"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  run              Run the PDF renamer (main.py)"
    echo "  test             Test regex patterns interactively (test_patterns.py)"
    echo "  bash             Start interactive bash shell in container"
    echo "  build            Build Docker image"
    echo "  logs             Show container logs"
    echo "  help             Show this help message"
    echo ""
}

case "${1:-run}" in
    run)
        docker-compose run --rm pdfnameforger
        ;;
    test)
        docker-compose run --rm -it pdfnameforger python /app/scripts/test_patterns.py
        ;;
    bash)
        docker-compose run --rm -it pdfnameforger bash
        ;;
    build)
        docker-compose build
        ;;
    logs)
        docker-compose logs -f
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
