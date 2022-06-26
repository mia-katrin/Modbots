using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.SideChannels;
using UnityEngine.SceneManagement;
using System.Collections;

public class GameManager : MonoBehaviour
{
    // singleton
    private static GameManager instance;
    public static GameManager Instance { get { return instance; } }

    public ComSideChannel pythonCom;

    public static int warmupFixedUpdates = 5;

    public ModularRobot modularRobot;
    public string currentGene = "";
    public bool resetting = false;
    public bool firstReset = true;

    public void Awake()
    {
        // Make sure there is only one instance of the game manager
        if (instance != null && instance != this)
        {
            this.gameObject.SetActive(false);
            Destroy(this.gameObject);
            return;
        }
        else if (instance == null)
        {
            instance = this;
        }
        DontDestroyOnLoad(gameObject);
        
        // We create the Side Channel
        if (pythonCom == null)
        {
            pythonCom = ComSideChannel.Instance;
            SideChannelsManager.RegisterSideChannel(pythonCom);
        }
        Academy.Instance.OnEnvironmentReset += ResetHappened;
        ComSideChannel.OnReceivedEncoding += NewEncodingGot;
    }

    private void NewEncodingGot(string gene)
    {
        currentGene = gene;
    }

    private void ResetHappened()
    {
        if (resetting || firstReset)
        {
            firstReset = false;
            return;
        }
        resetting = true;
        if (SceneManager.GetActiveScene().isLoaded)
        {
            SceneManager.LoadScene(0);
        }

        // Make robot
        // every scene load, a modular robot is made (becuse it belongs to the scene)
        // it is responsible for enforcing its singleton-ness itself
        modularRobot.DestroyContents();

        Resources.UnloadUnusedAssets();
        System.GC.Collect();

        StartCoroutine(CreateRobot());
    }

    public IEnumerator CreateRobot()
    {
        //pythonCom.SendMessage("GameManager starting coroutine");
        Physics.autoSimulation = false;
        for (int i = 0; i < warmupFixedUpdates; i++)
        {
            yield return new WaitForFixedUpdate();
        }

        if (currentGene.Length > 0) modularRobot.MakeRobot(currentGene);
        EnvironmentBuilder.Instance.BuildEnvironment();

        // By default, newly spawned objects are not synced with the physics world before the next pyhsics frame
        // Calling this forces that, so we can do collision checks
        Physics.SyncTransforms();
        yield return new WaitForFixedUpdate();
        if (currentGene.Length > 0) modularRobot.PruneCollisions();
        Physics.autoSimulation = true;

        string indexes = "Created modules: ";
        foreach (GameObject go in modularRobot.allModules)
        {
            indexes += go.GetComponent<ModuleParameterized>().index + ",";
        }
        pythonCom.SendMessage(indexes);

        string coor = "Coordinates: ";
        foreach (GameObject go in modularRobot.allModules)
        {
            coor += go.transform.GetChild(0).transform.position + ",";
        }
        pythonCom.SendMessage(coor);

        resetting = false;
    }

    private void OnDestroy()
    {
        if (Academy.IsInitialized && pythonCom != null)
        {
            SideChannelsManager.UnregisterSideChannel(pythonCom);
        }
    }

    public bool robotElseModule = false;
    int indexCounter = 0;
    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if (robotElseModule)
            {
                NewEncodingGot("Random");
                ResetHappened();
                    
            }
            else
            {
                modularRobot.DestroyContents();

                //for (int i = 0; i < 5; i++)
                //{
                //GameObject module = Instantiate(ModularRobot.Instance.modulePrefab);
                //ModuleParameterized rootModule = module.GetComponent<ModuleParameterized>();
                //rootModule.SetIndex(0);
                //rootModule.transform.position = new Vector3(2.5f - i,0, 0);
                //
                //rootModule.SetSize(0.1f + i*0.9f/2f);
                //rootModule.RemoveFixedJoint();
                //}

                GameObject module = Instantiate(ModularRobot.Instance.modulePrefab);
                ModuleParameterized rootModule = module.GetComponent<ModuleParameterized>();
                rootModule.SetIndex(indexCounter);
                indexCounter++;

                rootModule.SetSize(1f);
                rootModule.RemoveFixedJoint();
            }

            modularRobot.MaxStep = 10000000;
        }
    }
}