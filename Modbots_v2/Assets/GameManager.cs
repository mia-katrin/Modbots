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
        // Calling this forces that
        Physics.SyncTransforms();
        yield return new WaitForFixedUpdate();
        modularRobot.PruneCollisions();
        Physics.autoSimulation = true;

        string indexes = "Created modules: ";
        foreach (GameObject go in modularRobot.allModules)
        {
            indexes += go.GetComponent<ModuleParameterized>().index + ",";
        }
        //pythonCom.SendMessage(indexes);
        resetting = false;
    }

    private void OnDestroy()
    {
        if (Academy.IsInitialized && pythonCom != null)
        {
            SideChannelsManager.UnregisterSideChannel(pythonCom);
        }
    }

    public bool robotElseModule = true;
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
                GameObject module = Instantiate(ModularRobot.Instance.modulePrefab);
                ModuleParameterized rootModule = module.GetComponent<ModuleParameterized>();
                rootModule.SetIndex(0);

                rootModule.SetSize(1f);
                rootModule.RemoveFixedJoint();
            }

            modularRobot.MaxStep = 10000000;
        }
    }
}