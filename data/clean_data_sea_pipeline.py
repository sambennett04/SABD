import argparse
import codecs
import logging
import ujson
import sys
import os
from tqdm import tqdm

sys.path.append('.')

from data.bug_report_database import BugReportDatabase
from data.preprocessing import softClean

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_name', required=True, help="project name")
    parser.add_argument('--project_path', required=True, help="path for current project")
    parser.add_argument('--fields', nargs='+', help='A list of window sizes', required=True, default=["description"])

    parser.add_argument('--type', help='Option: agg (clean more aggressive the data), soft (put a space between words and punctuation, remove date)')
    parser.add_argument('--rm_punc', action="store_true")
    parser.add_argument('--rm_number', action="store_true")
    parser.add_argument('--sent_tok', action="store_true")
    parser.add_argument('--stop_words', action="store_true")
    parser.add_argument('--stem', action="store_true")
    parser.add_argument('--lower_case', action="store_true")
    parser.add_argument('--rm_char', action="store_true")

    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()
    logger.addHandler(logHandler)

    logger.info("Loading bug reports content")
    #loads the bugs from the json file
    bug_dataset = os.path.join(args.project_path, (args.project_name + ".jsonl"))
    bugReportDataset = BugReportDatabase.fromJson(bug_dataset)

    output = os.path.join(args.project_path, (args.project_name + "_soft_clean.jsonl"))

    newFile = codecs.open(output, "w", encoding='utf-8')

    nEmptyBugs = 0

    if args.type == 'soft':
        logger.info("Soft clean")
        cleanFunc = softClean
    else:
        logger.error("Type argument unknown")
        sys.exit(-1)

    logger.info("Cleaning Data")
    empty_bug_ids = set()

    #tqdm is just a progress bar, indicates what percentage of the bugs have been cleaned, ie. what loop itteration we are on

    #once for each bug

    cleaned_description_counter = 0
    for idx in tqdm(range(len(bugReportDataset))):

        #get the current bug
        bug = bugReportDataset.getBugByIndex(idx)

        #splits the current bug into a dictionary
        cleanBug = dict(bug)

        #for our example short desc and description

        

        for fieldName in args.fields:
            try:
                if len(bug[fieldName]) == 0:
                    continue
            except TypeError:
                print(bug['bug_id'])

            #length of string that represents either short desc or long desc of current bug
            l = len(bug[fieldName])

            #cleaning full description
            if fieldName == 'description':
                cleaned_description_counter += 1
                cleanBug[fieldName] = cleanFunc(bug[fieldName], args.rm_punc, args.sent_tok, \
                    args.rm_number, args.stop_words, args.stem, args.lower_case, args.rm_char)

            #cleaning shortened description
            else:
                cleanBug[fieldName] = cleanFunc(bug[fieldName], args.rm_punc, False, \
                    args.rm_number, args.stop_words, args.stem, args.lower_case, args.rm_char)

            if len(cleanBug[fieldName]) == 0:
                logger.info("Bug %s: %s content was erased!" % (bug['bug_id'], fieldName))
                nEmptyBugs += 1
        
        # if len(cleanBug['short_desc']) == 0 and len(cleanBug['description']) == 0:
        #     continue
        
        newFile.write(ujson.dumps(cleanBug))
        newFile.write("\n")

    #print("the number of descriptions cleaned: ", cleaned_description_counter)
    logging.info("Total number of new empty bugs: %d" % nEmptyBugs)
    logging.info("Finish!!!")