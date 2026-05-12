#!/usr/bin/env python3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Dummy pdc.py command")
    parser.add_argument("-i", nargs='+', metavar="ARGS", help="PDC number, [Optical port number, HIF number]")
    parser.add_argument("--hifr", nargs=2, metavar=("ADDRESS", "READ_SIZE"), help="Address, Read size")
    parser.add_argument("--pdcr", nargs=2, metavar=("ADDRESS", "WORDSIZE"), help="Address, Word size")

    args = parser.parse_args()

    if args.i and args.hifr:
        if len(args.i) < 3:
            print("Error: -i requires 3 arguments when using --hifr.", file=sys.stderr)
            sys.exit(1)
        try:
            pdc_num = int(args.i[0])
            port_num = int(args.i[1])
            hif_num = int(args.i[2])
        except ValueError:
            print("Error: -i arguments must be integers.", file=sys.stderr)
            sys.exit(1)

        try:
            addr = int(args.hifr[0], 0)
            read_size = int(args.hifr[1], 0)
        except ValueError:
            print("Error: --hifr arguments must be valid integers.", file=sys.stderr)
            sys.exit(1)

        # 範囲チェック
        if not (1 <= pdc_num <= 2):
            print(f"Error: PDC number must be 1 or 2, got {pdc_num}", file=sys.stderr)
            sys.exit(1)
        if not (1 <= port_num <= 4):
            print(f"Error: Optical port number must be between 1 and 4, got {port_num}", file=sys.stderr)
            sys.exit(1)
        if not (1 <= hif_num <= 8):
            print(f"Error: HIF number must be between 1 and 8, got {hif_num}", file=sys.stderr)
            sys.exit(1)

        # PDC1とPDC2で異なるダンプパターン
        dump_pdc1 = ["09", "10", "24", "20"]
        dump_pdc2 = ["17", "10", "24", "20"]
        
        target_dump = dump_pdc1 if pdc_num == 1 else dump_pdc2

        # read_size分だけダンプを返す。4バイトを超える場合は循環させる
        for i in range(read_size):
            val = target_dump[i % len(target_dump)]
            current_addr = addr + i
            print(f"{current_addr:04x}: {val}")

    elif args.i and args.pdcr:
        if len(args.i) < 1:
            print("Error: -i requires at least 1 argument when using --pdcr.", file=sys.stderr)
            sys.exit(1)
        try:
            pdc_num = int(args.i[0])
        except ValueError:
            print("Error: -i argument must be integer.", file=sys.stderr)
            sys.exit(1)

        try:
            addr = int(args.pdcr[0], 0)
            word_size = int(args.pdcr[1], 0)
        except ValueError:
            print("Error: --pdcr arguments must be valid integers.", file=sys.stderr)
            sys.exit(1)

        # 範囲チェック
        if not (1 <= pdc_num <= 2):
            print(f"Error: PDC number must be 1 or 2, got {pdc_num}", file=sys.stderr)
            sys.exit(1)

        for i in range(word_size):
            current_addr = addr + (i * 4)
            print(f"{current_addr:04x}: 20240404")

    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
