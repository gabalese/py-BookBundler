from __future__ import division  # for python < 3
import difflib
import warnings

LINE_MATH_THRESOLD = 0.6        # global sensible options
SOURCE_MATCH_THRESOLD = 0.6     # if required, can be changed at the module level
                                # to be stricter, eg. matching.LINE_MATCH_THRESOLD = 0.8


def matches(source, destination):
    """
    Basic mathing algorithm. Double iterating over src & dst lines, calculate the match ratio of each line couple
    and increase the counter for each sufficient match. If enough lines match, return true.

    :param source: list of input text
    :type source: list
    :param destination: list of reference text
    :type destination: list
    :rtype: bool
    """
    matching_counter = 0
    for i in source:
        for v in destination:
            if len(i) > 1 and len(v) > 1:
                warnings.filterwarnings('ignore')
                # avoid printing plenty of unicode warnings on stdout
                seq = difflib.SequenceMatcher(a=i.lower(), b=v.lower(), autojunk=True)
                # ... but just for this line
                warnings.resetwarnings()
            else:
                continue  # don't bother triying to match line abortions
            if float(seq.ratio()) >= LINE_MATH_THRESOLD:
                matching_counter += 1
            if map(len, i.split(" ")) == map(len, v.split(" ")):
                if i == v:
                    return True  # immediately return if a perfect match is found
    else:  # sum up at the end of iteration
        wAvg = matching_counter / len(source)
        # if more than x% of the source text lines match the destination text, source and destination match
        if wAvg >= SOURCE_MATCH_THRESOLD:
            return True
        else:
            return False
