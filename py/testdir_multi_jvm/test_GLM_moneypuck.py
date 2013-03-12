import os, json, unittest, time, shutil, sys, random
sys.path.extend(['.','..','py'])


import h2o, h2o_cmd, h2o_glm, h2o_hosts, h2o_glm
import h2o_browse as h2b, h2o_import as h2i


class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(1,java_heap_GB=8)
        else:
            h2o_hosts.build_cloud_with_hosts()

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_GLM_moneypuck(self):
        if 1==1:
            # None is okay for key2
            csvFilenameList = [
                ('hdb-2007-02-05/Goalies.csv',120,'Goalies'),
                ('hdb-2007-02-05/GoaliesSC.csv',120,'GoaliesSC'),
                # ('hdb-2007-02-05/Master.csv',120,'Master'),
                ('hdb-2007-02-05/Scoring.csv',120,'Scoring'),
                ('hdb-2007-02-05/ScoringSC.csv',120,'ScoringSC'),
                ('hdb-2007-02-05/Teams.csv',120,'Teams'),
                ('hdb-2007-02-05/TeamsHalf.csv',120,'TeamsHalf'),
                ('hdb-2007-02-05/TeamsPost.csv',120,'TeamsPost'),
                ('hdb-2007-02-05/TeamsSC.csv',120,'TeamsSC'),
                ('tricks-2012-06-23/HatTricks.csv',120,'HatTricks'),
                ('bkb090621/abbrev.csv',120,'abbrev'),
                ('bkb090621/AwardsCoaches.csv',120,'AwardsCoaches'),
                ('bkb090621/AwardsPlayers.csv',120,'AwardsPlayers'),
                ('bkb090621/Coaches.csv',120,'Coaches'),
                # never finishes?
                # ('bkb090621/Draft.csv',120,'Draft'),
                # ('bkb090621/Master.csv',120,'Master'),
                ('bkb090621/PlayersAllstar.csv',120,'PlayersAllstar'),
                ('bkb090621/Players.csv',120,'Players'),
                ('bkb090621/PlayersPlayoffs.csv',120,'PlayersPlayoffs'),
                ('bkb090621/Teams.csv',120,'Teams'),
                ('hdb-2007-02-05/abbrev.csv',120,'abbrev'),
                # SPD without regularization
                # can't solve, when regularization added
                # ('hdb-2007-02-05/AwardsCoaches.csv',120,'AwardsCoaches'),
                # ('hdb-2007-02-05/AwardsMisc.csv',120,'AwardsMisc'),
                ('hdb-2007-02-05/AwardsPlayers.csv',120,'AwardsPlayers'),
                # can't solve, when regularization added
                # ('hdb-2007-02-05/Coaches.csv',120,'Coaches'),
                ]

        # a browser window too, just because we can
        h2b.browseTheCloud()

        importFolderPath = '/home/0xdiag/datasets/hockey'
        h2i.setupImportFolder(None, importFolderPath)
        for csvFilename, timeoutSecs, key2 in csvFilenameList:
            # creates csvFilename.hex from file in importFolder dir 
            parseKey = h2i.parseImportFolderFile(None, csvFilename, importFolderPath, timeoutSecs=2000, key2=key2)
            inspect = h2o_cmd.runInspect(None, parseKey['destination_key'])
            csvPathname = importFolderPath + "/" + csvFilename
            num_rows = inspect['num_rows']
            num_cols = inspect['num_cols']

            print "\n" + csvPathname, \
                "    num_rows:", "{:,}".format(num_rows), \
                "    num_cols:", "{:,}".format(num_cols)

            max_iter = 30 
            # assume the last col is the output!
            y = num_cols-1
            kwargs = {
                'y': y, 
                'family': 'poisson',
                'link': 'log',
                'num_cross_validation_folds': 0, 
                'max_iter': max_iter, 
                'beta_epsilon': 1e-3}

            # L2 
            if 1==0:
                kwargs.update({'alpha': 0, 'lambda': 0})
                start = time.time()
                glm = h2o_cmd.runGLMOnly(parseKey=parseKey, timeoutSecs=timeoutSecs, **kwargs)
                print "glm (L2) end on ", csvPathname, 'took', time.time() - start, 'seconds'
                # assume each one has a header and you have to indirect thru 'column_names'
                column_names = glm['GLMModel']['column_names']
                print "column_names[0]:", column_names[0]
                h2o_glm.simpleCheckGLM(self, glm, None, **kwargs)
                h2b.browseJsonHistoryAsUrlLastMatch("GLM")


            # Elastic
            kwargs.update({'alpha': 0.5, 'lambda': 1e-4})
            start = time.time()
            glm = h2o_cmd.runGLMOnly(parseKey=parseKey, timeoutSecs=timeoutSecs, **kwargs)
            print "glm (Elastic) end on ", csvPathname, 'took', time.time() - start, 'seconds'
            h2o_glm.simpleCheckGLM(self, glm, None, **kwargs)

            # L1
            kwargs.update({'alpha': 1.0, 'lambda': 1e-4})
            start = time.time()
            glm = h2o_cmd.runGLMOnly(parseKey=parseKey, timeoutSecs=timeoutSecs, **kwargs)
            print "glm (L1) end on ", csvPathname, 'took', time.time() - start, 'seconds'
            h2o_glm.simpleCheckGLM(self, glm, None, **kwargs)


if __name__ == '__main__':
    h2o.unit_main()
